import os
from datetime import datetime
import site
import operator
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# get modules for math operations
from numpy import mean
from numpy import median
from numpy import vdot as vector_product
from numpy import sqrt
from numpy import histogram
import math
# get access to local helper functions
from config import config
# JSON functionality
import simplejson as json

# General functions
def sort_list_of_lists(L, index, rvrs=True):
    """
    Sort a list of lists with 'index' as sort key
    """
    return sorted(L, key=operator.itemgetter(index), reverse=rvrs)

def get_timespan(biblist):
    """
    Returns the time span (years) for a list of bibcodes
    """
    years = map(lambda a: int(a[:4]), biblist)
    minYr = min(years)
    maxYr = max(years)
    span  = maxYr - minYr + 1
    return max(span,1)

def get_subset(mlist,year):
    """
    Gets the entries out of the list of "attribute" vectors for a certain year
    """
    newlist = []
    for entry in mlist:
        if int(entry[0][:4]) > int(year):
            continue
        newvec = entry[:8]
        citations = entry[8]['citations']
        citations = filter(lambda a: int(a[:4]) <= int(year), citations)
        newvec[2]  = len(citations)
        newlist.append(newvec)
    return newlist

#### Abstract data models:
# Every abstract model contains machinery to calculate the appropriate statistics,
# implemented in the 'generate_data' method.
# How the data are provided is implemented in every specific class that inherits from
# the general model class, by implementing a specific 'pre_process' method. Similarly, the
# specific results are implemented by overloading the general 'post_process' method.
class Statistics():
    """
    Statistics class calculates statistics for a list of numbers and 
    associated weights.
    Input data consists of Python list: 
        L = [..., (number, weight), ...], 
    so that the frequency for item k is L[k][0], and the weight for 
    item k is l[k][1]  (k=0,...,N).
    """
    @classmethod
    def generate_data(cls):
        """
        get statistics for a list of values and associated weights:
            mean, median, normalized values
        """
        cls.pre_process()
        #
        values = map(lambda a: a[0], cls.data)
        weights= map(lambda a: a[1], cls.data)
        refereed_values = map(lambda a: a[0], cls.refereed_data)
        refereed_weights= map(lambda a: a[1], cls.refereed_data)
        # get number of entries
        cls.number_of_entries = len(values)
        # get number of refereed entries
        cls.number_of_refereed_entries = len(refereed_values)
        # get normalized value
        cls.normalized_value = float('%.1f' % round(vector_product(values,weights), 1))
        # get refereed normalized value
        cls.refereed_normalized_value = float('%.1f' % round(vector_product(refereed_values,refereed_weights), 1))
        # get mean value of values
        if len(values) != 0:
            cls.mean_value = float('%.1f' % round(mean(values), 1))
        else:
            cls.mean_value = 0
        # get mean value of refereed values
        if len(refereed_values) != 0:
            cls.refereed_mean_value = float('%.1f' % round(mean(refereed_values), 1))
        else:
            cls.refereed_mean_value = 0.0
        # get median value of values
        if len(values) != 0:
            cls.median_value = float('%.1f' % round(median(values), 1))
        else:
            cls.median_value = 0.0
        # get median value of refereed values
        if len(refereed_values) != 0:
            cls.refereed_median_value = float('%.1f' % round(median(refereed_values), 1))
        else:
            cls.refereed_median_value = 0.0
        # get total of values
        cls.total_value = sum(values)
        # get total of refereed values
        cls.refereed_total_value = sum(refereed_values)
        # record results
        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

# Metrics class

# to calculate tori:
#    tori_list = [item for sublist in cit_dict.values() for item in sublist]
#    print sum(map(lambda c: 1.0/float(c), map(lambda b: max(b[1],config.METRICS_MIN_BIBLIO_LENGTH)*b[2],filter(lambda a: len(a) > 0, tori_list))))

class Metrics():

    @classmethod
    def generate_data(cls):
        cls.pre_process()
        # array with citations, descending order
        citations = cls.citations
        citations.sort()
        citations.reverse()
        # first calclate the Hirsch and g indices
        rank = 1
        N = 0
        h = 0
        g = 0
        for cite in citations:
            N += cite
            r2 = rank*rank
            if r2 <= N:
                g = rank
            h += min(1, cite/rank)
            rank += 1
        # the e-index
        try:
            e = sqrt(sum(citations[:h]) - h*h)
        except:
            e = 'NA'
        # Get the number of self-citations
        try:
            number_of_self_citations = sum(map(lambda a: a['number_of_self_citations'], cls.metrics_data))
        except:
            number_of_self_citations = 0
        # get the Tori index
        rn_citations = map(lambda a: a['rn_citations'], cls.metrics_data)
        auth_nums    = map(lambda a: 1.0/float(a['author_num']), cls.metrics_data)
        tori = vector_product(rn_citations,auth_nums)
        try:
            read10_reads = map(lambda a: a[7][-2], cls.reads10data)
            read10_auths = map(lambda a: 1.0/float(a[4]), cls.reads10data)
            read10 = vector_product(read10_reads, read10_auths)
        except:
            read10 = 0
        try:
            riq = int(1000.0*sqrt(float(tori))/float(cls.time_span))
        except:
            riq = "NA"
        cls.h_index = h
        cls.g_index = g
        cls.m_index = float('%.1f' % round(float(h)/float(cls.time_span), 2))
        cls.i10_index = len(filter(lambda a: a >= 10, citations))
        cls.i100_index= len(filter(lambda a: a >= 100, citations))
        cls.e_index = float('%.1f' % round(e,1))
        cls.tori = float('%.1f' % round(tori,1))
        cls.riq  = float('%.1f' % round(riq,1))
        cls.read10 = int(round(read10))
        cls.number_of_self_citations = number_of_self_citations

        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

# Histogram class
class Histogram():

    @classmethod
    def generate_data(cls):
        """
        Get histogram for a list of values and associated weights
        The weights are used for a normalized histogram
        """
        cls.results = {}
        cls.pre_process()
        today = datetime.today()
        skip = None
        values = map(lambda a: a[0], cls.data)
        if len(values) == 0 and 'citation' not in cls.config_data_name:
            skip = True
        weights= map(lambda a: a[1], cls.data)
        if cls.config_data_name == 'reads_histogram':
            bins = range(1996, today.year+2)
        elif cls.min_year:
            bins = range(cls.min_year, today.year+2)
        else:
            try:
                bins = range(min(values),max(values)+2)
            except:
                skip = True
        if not skip:
            refereed_values = map(lambda a: a[0], cls.refereed_data)
            refereed_weights= map(lambda a: a[1], cls.refereed_data)
            # get the regular histogram
            cls.value_histogram = histogram(values,bins=bins)
            cls.refereed_value_histogram = histogram(refereed_values,bins=bins)
            # get the normalized histogram
            cls.normalized_value_histogram = histogram(values,bins=bins,weights=weights)
            cls.refereed_normalized_value_histogram = histogram(refereed_values,bins=bins,weights=refereed_weights)
        else:
            cls.value_histogram = False
            cls.results[str(today.year)] = "0:0:0:0"
        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

# Time Series class
class TimeSeries():

    @classmethod
    def generate_data(cls):
        """
        Get time series
        """
        today = datetime.today()
        bibcodes = map(lambda a: a[0], cls.attributes)
        years = map(lambda a: int(a[:4]), bibcodes)
        minYear = min(years)
        maxYear = today.year
        cls.series = {}
        cls.pre_process()
        for year in range(minYear, maxYear+1):
            if year < 1996:
                read10 = 0
            else:
                threshold = year - 10
                year_index = year - 1996
                if year == maxYear:
                    year_index -= 1
                reads10data = filter(lambda a: len(a[7]) > 0 and int(a[0][:4]) > threshold, cls.attributes)
                try:
                    read10_reads = map(lambda a: a[7][year_index], reads10data)
                    read10_auths = map(lambda a: 1.0/float(a[4]), reads10data)
                    read10 = vector_product(read10_reads, read10_auths)
                except:
                    read10 = 0
            tori = sum([value for d in cls.metrics_data for (yr,value) in d['rn_citations_hist'].items() if int(yr) <= year])
            new_list = get_subset(cls.attributes,year)
            new_list = sort_list_of_lists(new_list,2)
            citations = map(lambda a: a[2], new_list)
            # first calclate the Hirsch and g indices
            rank = 1
            N = 0
            h = 0
            g = 0
            for cite in citations:
                N += cite
                r2 = rank*rank
                if r2 <= N:
                    g = rank
                h += min(1, cite/rank)
                rank += 1
            TimeSpan = year - minYear + 1
            i10 = len(filter(lambda a: a >= 10, citations))
            i100= len(filter(lambda a: a >= 100, citations))
            m = float(h)/float(TimeSpan)
            roq = int(1000.0*math.sqrt(float(tori))/float(TimeSpan))
            indices = "%s:%s:%s:%s:%s:%s:%s:%s" % (h,g,i10,tori,m,roq,i100,int(round(read10)*0.1))
            cls.series[str(year)] = indices

        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

#### Classes specific to bibliographic data:
#
class PublicationStatistics(Statistics):
    config_data_name = 'publications'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            data.append((1,weight))
            if vector[1]:
                refereed_data.append((1,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Number of papers (Total)'] = cls.number_of_entries
        cls.results['Normalized paper count (Total)'] = cls.normalized_value
        cls.results['Number of papers (Refereed)'] = cls.number_of_refereed_entries
        cls.results['Normalized paper count (Refereed)'] = cls.refereed_normalized_value

class ReadsStatistics(Statistics):
    config_data_name = 'reads'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Nreads = vector[5]
            data.append((Nreads,weight))
            if vector[1]:
                refereed_data.append((Nreads,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Total number of reads (Total)'] = cls.total_value
        cls.results['Average number of reads (Total)'] = cls.mean_value
        cls.results['Median number of reads (Total)'] = cls.median_value
        cls.results['Normalized number of reads (Total)'] = cls.normalized_value
        cls.results['Total number of reads (Refereed)'] = cls.refereed_total_value
        cls.results['Average number of reads (Refereed)'] = cls.refereed_mean_value
        cls.results['Median number of reads (Refereed)'] = cls.refereed_median_value
        cls.results['Normalized number of reads (Refereed)'] = cls.refereed_normalized_value

class DownloadsStatistics(Statistics):
    config_data_name = 'downloads'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            bbc = vector[0]
            weight = 1.0/float(vector[4])
            Nreads = vector[6]
            data.append((Nreads,weight))
            if vector[1]:
                refereed_data.append((Nreads,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Total number of downloads (Total)'] = cls.total_value
        cls.results['Average number of downloads (Total)'] = cls.mean_value
        cls.results['Median number of downloads (Total)'] = cls.median_value
        cls.results['Normalized number of downloads (Total)'] = cls.normalized_value
        cls.results['Total number of downloads (Refereed)'] = cls.refereed_total_value
        cls.results['Average number of downloads (Refereed)'] = cls.refereed_mean_value
        cls.results['Median number of downloads (Refereed)'] = cls.refereed_median_value
        cls.results['Normalized number of downloads (Refereed)'] = cls.refereed_normalized_value

class TotalCitationStatistics(Statistics):
    config_data_name = 'citations'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        citing_papers = []
        citing_papers_refereed = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Ncites = vector[2]
            data.append((Ncites,weight))
            if vector[1]:
                refereed_data.append((Ncites,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Number of citing papers (Total)'] = cls.num_citing
        cls.results['Total citations (Total)'] = cls.total_value
        cls.results['Average citations (Total)'] = cls.mean_value
        cls.results['Median citations (Total)'] = cls.median_value
        cls.results['Normalized citations (Total)'] = cls.normalized_value
        cls.results['Number of citing papers (Refereed)'] = cls.num_citing_ref
        cls.results['Total citations (Refereed)'] = cls.refereed_total_value
        cls.results['Average citations (Refereed)'] = cls.refereed_mean_value
        cls.results['Median citations (Refereed)'] = cls.refereed_median_value
        cls.results['Normalized citations (Refereed)'] = cls.refereed_normalized_value

class RefereedCitationStatistics(Statistics):
    config_data_name = 'refereed_citations'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Ncites = vector[3]
            data.append((Ncites,weight))
            if vector[1]:
                refereed_data.append((Ncites,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Refereed citations (Total)'] = cls.total_value
        cls.results['Average refereed citations (Total)'] = cls.mean_value
        cls.results['Median refereed citations (Total)'] = cls.median_value
        cls.results['Normalized refereed citations (Total)'] = cls.normalized_value
        cls.results['Refereed citations (Refereed)'] = cls.refereed_total_value
        cls.results['Average refereed citations (Refereed)'] = cls.refereed_mean_value
        cls.results['Median refereed citations (Refereed)'] = cls.refereed_median_value
        cls.results['Normalized refereed citations (Refereed)'] = cls.refereed_normalized_value

class TotalMetrics(Metrics):
    config_data_name = 'metrics'
    # Tori follows from 'rn_normalized' citation values and the inverse author number for each paper
    @classmethod
    def pre_process(cls):
        today = datetime.today()
        threshold = today.year - 10
        cls.reads10data = filter(lambda a: len(a[7]) > 0 and int(a[0][:4]) > threshold, cls.attributes)
        biblist = map(lambda a: a[0], cls.attributes)
        cls.time_span = get_timespan(biblist)
        cls.refereed = 0
        cls.citations = map(lambda a: a[2], cls.attributes)
        cls.metrics_data = map(lambda a: a[8], cls.attributes)

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['H-index (Total)'] = cls.h_index
        cls.results['g-index (Total)'] = cls.g_index
        cls.results['m-index (Total)'] = cls.m_index
        cls.results['i10-index (Total)'] = cls.i10_index
        cls.results['i100-index (Total)'] = cls.i100_index
        cls.results['e-index (Total)'] = cls.e_index
        cls.results['tori index (Total)'] = cls.tori
        cls.results['roq index (Total)'] = cls.riq
        cls.results['read10 index (Total)'] = cls.read10
        cls.results['self-citations (Total)'] = cls.number_of_self_citations

class RefereedMetrics(Metrics):
    config_data_name = 'refereed_metrics'

    @classmethod
    def pre_process(cls):
        today = datetime.today()
        threshold = today.year - 10
        cls.reads10data = filter(lambda a: len(a[7]) > 0 and a[1] == 1 and int(a[0][:4]) > threshold, cls.attributes)
        biblist = map(lambda a: a[0], cls.attributes)
        cls.time_span = get_timespan(biblist)
        cls.refereed = 1
        cls.citations = map(lambda b: b[2],
                           filter(lambda a: a[1] == 1, cls.attributes))
        cls.metrics_data = map(lambda b: b[8], filter(lambda a: a[1] == 1, cls.attributes))

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['H-index (Refereed)'] = cls.h_index
        cls.results['g-index (Refereed)'] = cls.g_index
        cls.results['m-index (Refereed)'] = cls.m_index
        cls.results['i10-index (Refereed)'] = cls.i10_index
        cls.results['i100-index (Refereed)'] = cls.i100_index
        cls.results['e-index (Refereed)'] = cls.e_index
        cls.results['tori index (Refereed)'] = cls.tori
        cls.results['roq index (Refereed)'] = cls.riq
        cls.results['read10 index (Refereed)'] = cls.read10
        cls.results['self-citations (Refereed)'] = cls.number_of_self_citations

class PublicationHistogram(Histogram):
    config_data_name = 'publication_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            year = int(vector[0][:4])
            weight = 1.0/float(vector[4])
            if vector[1]:
                refereed_data.append((year,weight))
            data.append((year,weight))
        cls.data = data
        cls.refereed_data = refereed_data
        cls.min_year = ''

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res

class ReadsHistogram(Histogram):
    config_data_name = 'reads_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vec in cls.attributes:
            Nreads = len(vec[7])
            for i in range(Nreads):
                for j in range(vec[7][i]):
                    data.append((1996+i,1.0/float(vec[4])))
                    if vec[1]:
                        refereed_data.append((1996+i,1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data
        cls.min_year = ''

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res

class AllCitationsHistogram(Histogram):
    '''
    This part of the citations histogram contains
    the all citations to both refereed and
    non-refereed papers
    '''
    config_data_name = 'all_citation_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        min_year = 9999
        for vec in cls.attributes:
            min_year = min(int(vec[0][:4]), min_year)
            for citation in vec[8]['citations']:
                data.append((int(citation[:4]), 1.0/float(vec[4])))
                if vec[1]:
                    refereed_data.append((int(citation[:4]), 1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data
        cls.min_year = min_year

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res.split(':')

class RefereedCitationsHistogram(Histogram):
    '''
    This part of the citations histogram contains
    the refereed citations to both refereed and
    non-refereed papers
    '''
    config_data_name = 'refereed_citation_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        min_year = 9999
        for vec in cls.attributes:
            min_year = min(int(vec[0][:4]), min_year)
            for citation in vec[8]['refereed_citations']:
                data.append((int(citation[:4]), 1.0/float(vec[4])))
                if vec[1]:
                    refereed_data.append((int(citation[:4]), 1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data
        cls.min_year = min_year

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res.split(':')

class NonRefereedCitationsHistogram(Histogram):
    '''
    This part of the citations histogram contains
    the non-refereed citations to both refereed and
    non-refereed papers
    '''
    config_data_name = 'non_refereed_citation_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        min_year = 9999
        for vec in cls.attributes:
            min_year = min(int(vec[0][:4]), min_year)
            for citation in filter(lambda a: a not in vec[8]['refereed_citations'], vec[8]['citations']):
                data.append((int(citation[0][:4]), 1.0/float(vec[4])))
                if vec[1]:
                    refereed_data.append((int(citation[0][:4]), 1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data
        cls.min_year = min_year

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res.split(':')

class MetricsSeries(TimeSeries):
    config_data_name = 'metrics_series'

    @classmethod
    def pre_process(cls):
        cls.metrics_data = []
        # divide the values of the reference-normalized citation histogram by the number of
        # authors of cited paper (so that Tori is just sum of the values)
        for md in map(lambda a: a[8], cls.attributes):
            md['rn_citations_hist'].update((k,float(v)/float(md['author_num'])) for k, v in md['rn_citations_hist'].items())
            cls.metrics_data.append(md)

    @classmethod
    def post_process(cls):
        cls.results = cls.series
        cls.results['type'] = cls.config_data_name
