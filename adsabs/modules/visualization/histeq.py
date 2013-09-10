'''
histogram equalization for sequence of numbers
'''

class HistEq(object):
    """Implementation of the histogram equalization for a simple sequence of numbers and not images"""
    #range where I want to map the dfinal results
    
    def __init__(self, numseq, myrange=[1,10]):
        """Constructor"""
        self.orig_list = numseq
        self.numseq =  numseq.values()
        self.numseq_unique =  list(set(self.numseq))
        self.numseq_len = len(self.numseq)
        self.myrange = myrange
        self.occurrences = self.__get_occurrences()
        
        
    def __get_occurrences(self):
        """Method to speed up the method __probability_of_occurrence:
            I pre-compute the occurrences of each number
        """
        occurrences = {}
        if len(self.numseq_unique) > 0:
            for num in range(0, max(self.numseq_unique) + 1):
                occurrences[num] = self.numseq.count(num)
        return occurrences
    
    def __probability_of_occurrence(self, num):
        """Method that extract the probability of an occurrence of a number in the sequence:
            Px(i) = P(x=i) = Ni/N, 0<= i < L
            L being the total number of elements in the list
        """
        #I get the number of entries in the list
        N = self.numseq_len
        #I get the number of times num is in the list = Ni
        Ni = self.occurrences[num]
        
        return float(Ni)/float(N)
    
    def __cumulative_distribution_function(self, num):
        """defininition of the cumulative distribution function corresponding to Px as
            CDFx(i) = SUM (from j=0 to i) of Px(j)
        """
        sum = 0
        for j in range(0, num+1):
            sum = sum + self.__probability_of_occurrence(j)
        return sum
    
    def __normalize_into_interval(self, locdic):
        """Methon to map a list of numbers in a dictionary to a prefixed range"""
        #definition of the new range
        myrange = self.myrange
        #I extract the values from the dictionary
        myvalues = locdic.values()
        #I extract the maximun and the minimum value of the dictionary
        minvalue = min(myvalues)
        maxvalue = max(myvalues)
        
        #if max and min are the same, there is no need to do anything
        if minvalue == maxvalue:
            return locdic
        
        #I calculate the 2 constants I need to map the numbers I have into the new numbers on the new range
        #the 2 constants are calculated solving the system 
        #{ ax + b = x'
        #{ ay + b = y'
        #to find these constants (a and b) I first consider x and y like the min and max of the range of numbers I have
        #and x' and y' the min and max of the new range I want to have
        # then all the other numbers I have to calculate can be mapped with the formula
        # new_num = a*old_num + b
        
        a = (1/float(minvalue)) * (float(myrange[0]) - (((float(myrange[0])*float(maxvalue))-(float(myrange[1])*float(minvalue)))/(float(maxvalue) - float(minvalue))))
        b = ((float(myrange[0]) * float(maxvalue)) - (float(myrange[1]) * float(minvalue))) / (float(maxvalue) - float(minvalue))
        
        #than I map all the new values
        mapping = {}
        for old_num in myvalues:
            #I calculate the mapping for the new number
            new_num = a*old_num + b
            #then I put it in a dictionary
            mapping[str(old_num)] = new_num
        
        #then I set the new values for the original dictionary
        newlocdic = {}
        for elem in locdic:
            newlocdic[elem] = mapping[str(locdic[elem])]
            
        return newlocdic
        
    def hist_eq(self):
        """Main method of the class"""
        
        #I extract the max and the min values for the list of values
        try:
            maxlist = max(self.numseq)
        except:
            #in case of error there is nothing to do
            return {}
        
        try:
            minlist = min(self.numseq)
        except:
            #in case of error there is nothing to do
            return {}
            
        #I create a new dictionary for the results
        newdict = {}
        
        #for each number
        for num in self.numseq_unique:
            #I extract the probability to find the number in the list
            cdf = self.__cumulative_distribution_function(num)
            #I calculate the normalization for the number
            yfirst = (cdf * (maxlist - minlist)) + minlist
            
            #!!!!!! SBAGLIATO: se cambio i numeri nell'array originario e poi ho un nuovo numero che viene mappato da un altro nuvo numero, lo cambio 2 volte!
            # devo trovare un modo piu' safe per fare questa cosa
            for elem in self.orig_list:
                if self.orig_list[elem] == num:
                    newdict[elem] = yfirst
        
        normdict = self.__normalize_into_interval(newdict)
        
        return normdict
    
    
    