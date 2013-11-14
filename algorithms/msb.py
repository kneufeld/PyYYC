from scipy import stats
import numpy as np
import random
from django.db.models import Avg, StdDev, Count
from .models import Patient, MSBLog

class MSB(object):
    """Minimum sufficient total balancing randomization algorithm for allocation to A or B."""

    def __init__(self, obj, Patients, pklimit=0.1, e=0.4):
        """
        Process and validate the information required to complete the randomization.
        """
        # The patient that is being randomized
        self.obj = obj
        # The existing patients with the same tPA status as our patient
        self.Patients = Patients.filter(IVtPA=obj.IVtPA)
        # Set number of patients in tPA group of our patient
        self.IVtPA_Count = Patients.filter(IVtPA=obj.IVtPA).count()
        # Make a clone of GroupA queryset
        self.GroupA = self.Patients.filter(Group=0)._clone()
        # Make a clone of GroupB queryset
        self.GroupB = self.Patients.filter(Group=1)._clone()
        # Set the pklimit
        self.pklimit = pklimit
        # Set the e value
        self.e = e

        self.log = []

    def ContinuousVariable(self, k, xk, xka, xkb, ska, skb, na, nb, arrayA, arrayB):
        """ 
        Decide the vote for a continuous variable.

        :param k:
            String containing the variable to be tested.

        :param xk:
            Value of X for the individual who is to be randomized.

        :param xka:
            Mean value of k in Group A.

        :param xkb:
            Mean value of k in Group B.

        :param ska:
            Standard deviation of k in Group A.

        :param skb:
            Standard deviation of k in Group B.

        :param na:
            Number of people in Group A.

        :param nb:
            Number of people in Group B.

        tk = (xka - xkb) / ( (ska^2/na) + (skb^2)/nb )^(1/2)

        """
        # Calculate a t-test
        test = stats.ttest_ind(arrayA, arrayB)
        
        # Calculate the t-statistic manually
        tk = (xka - xkb) / ((((ska**2)/na) + ((skb**2))/nb ) ** (0.5))
        
        new_dict = {}
        new_dict['k'] = k
        new_dict['t_calc'] = test[0]
        new_dict['t_manual'] = tk
        new_dict['xk'] = xk
        new_dict['xka'] = xka
        new_dict['xkb'] = xkb

        tk = test[0]
        pk = test[1]
        
        # Does the p-value meet the cutoff?
        if (pk < self.pklimit):
            print "Significant T-test"
            
            # B group average is higher
            if (tk < 0):
                # xk is more than B average - Vote A
                if (xk > xkb):
                    Vote = 0
                # xk is less than A average - Vote B
                elif (xk < xka):
                    Vote = 1

            # A group average is higher
            elif (tk > 0):
                # xk is less than B average - Vote A
                if (xk < xkb):
                    Vote = 0
                # xk is more than A average - Vote B
                elif (xk > xka):
                    Vote = 1

        #********** -- OLD LOGIC FROM MANUAL tklimit APPROACH -- **********#
        # Logic for Vote A
        # if ((tk < (-self.tklimit)) and (xk > xkb)) or ((tk > self.tklimit) and (xk < xkb)):
        #   Vote = 0

        # # Logic for Vote B
        # elif ((tk < (-self.tklimit)) and (xk < xka)) or ((tk > self.tklimit) and (xk > xka)):
        #   Vote = 1
        #********** -- -------------------------------------- -- **********#

        # Neither of the vote logic were satisfied
        else:
            print "T-test Not Significant"
            Vote = None

        new_dict['Vote'] = Vote

        self.log.append(new_dict)
        # Return the vote
        return Vote


    def CategoricalVariable(self, k, A, B, DataTable):
        """ 
        Decide the vote for a categorical variable.

        :param k:
            String containing the variable to be tested.

        :param DataTable:
            The array of cell counts to be used in the chi-square test.

        """
        # Turn DataTable into a proper array
        obs = np.array(DataTable)
        # Calculate the chi-squared test
        chisquare = stats.chi2_contingency(obs)

        # Set the p-value from the chi-squared
        pk = chisquare[1]
        
        # Set the expected and observed values for Group A of the patient's category
        Ekja = chisquare[3][0][0]
        nkja = obs[0][0]

        # Set the expected and observed values for Group B of the patient's category
        Ekjb = chisquare[3][0][1]
        nkjb = obs[0][1]

        new_dict = {}
        new_dict['k'] = k
        new_dict['Ekja'] = Ekja
        new_dict['nkja'] = nkja
        new_dict['Ekjb'] = Ekjb
        new_dict['nkjb'] = nkjb


        if (pk < self.pklimit) and (Ekja > nkja):
            print "Significant chi-squared"
            Vote = 0

        elif (pk < self.pklimit) and (Ekjb > nkjb):
            print "Significant chi-squared"
            Vote = 1

        else:
            print "Not significant chi-squared"
            Vote = None

        new_dict['Vote'] = Vote

        self.log.append(new_dict)

        return Vote


    def prep_continuous(self, factor):
        """
        Prepare the kwargs for a Continuous Variable Vote determination
        """
        prepped_value = {}
        prepped_value['k'] = factor
        prepped_value['xk'] = getattr(self.obj, factor)
        prepped_value['xka'] = self.GroupA.aggregate(Avg(factor)).values()[0]
        prepped_value['xkb'] = self.GroupB.aggregate(Avg(factor)).values()[0]
        prepped_value['ska'] = self.GroupA.aggregate(StdDev(factor)).values()[0]
        prepped_value['skb'] = self.GroupB.aggregate(StdDev(factor)).values()[0]
        prepped_value['na'] = self.GroupA.count()
        prepped_value['nb'] = self.GroupB.count()
        prepped_value['arrayA'] = np.array(self.GroupA.values_list(factor, flat=True))
        prepped_value['arrayB'] = np.array(self.GroupB.values_list(factor, flat=True))
        return prepped_value


    def prep_categorical(self, factor):
        """
        Prepare the kwargs for a Categorical Variable Vote determination
        """
        prepped_value = {}
        AGroupFirst = []
        AGroup = []
        BGroupFirst = []
        BGroup = []
        # Set which category the patient is apart of
        patient_group = getattr(self.obj, factor)
        
        # If the category is actually a FK to an object then use its pk
        if hasattr(patient_group, 'pk'):
            patient_group = getattr(patient_group, 'pk')

        prepped_value['k'] = factor
        
        # Sort the counts so that the values will be in the same order in both groups
        A = self.GroupA.values(factor).annotate(count=Count(factor))
        A = sorted(A, key=lambda k: k[factor])
        
        # Sort the counts so that the values will be in the same order in both groups
        B = self.GroupB.values(factor).annotate(count=Count(factor))
        B = sorted(B, key=lambda k: k[factor])

        # Arrange the list so that the group the patient in is first
        for value in A:
            if value[factor] == patient_group:
                AGroupFirst.append(value['count'])
            else:
                AGroup.append(value['count'])   
        
        for value in B:
            if value[factor] == patient_group:
                BGroupFirst.append(value['count'])
            else:
                BGroup.append(value['count'])
        
        prepped_value['A'] = AGroupFirst+AGroup
        prepped_value['B'] = BGroupFirst+BGroup
        prepped_value['DataTable'] = zip(prepped_value['A'], prepped_value['B'])
        return prepped_value


    def VoteCount(self, factors={'Continuous': [], 'Categorical': []}):
        """
        Iterate through the factors and count the number of votes for each.
        """
        # Setup the dictionary that will count the votes for each of the groups.
        Vote_Counts = {0:0, 1:0, None:0}

        # Count the Continuous variable votes
        for factor in factors['Continuous']:
            Vote = self.ContinuousVariable(**self.prep_continuous(factor))
            print "%s Vote: " % factor, Vote
            try:
                Vote_Counts[Vote] += 1
            except:
                pass

        # Count the Categorical variable votes
        for factor in factors['Categorical']:
            Vote = self.CategoricalVariable(**self.prep_categorical(factor))
            print "%s Vote: " % factor, Vote
            try:
                Vote_Counts[Vote] += 1
            except:
                pass

        self.log.append({'Vote_Counts': Vote_Counts})

        return Vote_Counts


    def Decision(self, cutoff):
        """
        Returns 0 or 1 based on the provided cutoff value.
        """
        prob = random.random()
        self.log.append({'prob': prob})

        if prob > cutoff:
            decision = 0
        elif prob < cutoff:
            decision = 1
        else:
            decision = self.Decision(cutoff)

        self.log.append({'decision': decision})
        return decision


    def Determine_cutoff(self):
        factors = {}
        factors['Continuous'] = ['Age', 'BaselineNIHSS']
        factors['Categorical'] = ['Sex', 'BaselineASPECTS', 'BaselineOcclusionLocation', 'Site']
        Vote_Counts = self.VoteCount(factors)
        
        # If A > B
        if Vote_Counts[0] > Vote_Counts[1]:
            print "Skew For A"
            cutoff = self.e
        # If A < B
        elif Vote_Counts[0] < Vote_Counts[1]:
            print "Skew For B"
            cutoff = (1-self.e)
        # Neither was favoured
        else:
            print "Keep 50/50"
            cutoff = 0.5

        self.log.append({'cutoff': cutoff}) 
        return cutoff

    # def save_log(self):
    #   # MSBLog
    #   MSBLog.objects.create(patient=self.obj, log=self.log)
    #   return True

    def Randomizer(self):
        """
        Determines if MSB should be used or not.
        """
        # Get the number of subjects in the
        if self.IVtPA_Count > 20:
            try:
                cutoff = self.Determine_cutoff()
            except:
                self.log.append({'error': 'Determine_Cutoff failed'})
                cutoff = 0.5
        else:
            cutoff = 0.5

        Decision = self.Decision(cutoff)

        self.log.append({'e': self.e, 'pklimit': self.pklimit})

        return Decision, self.log




