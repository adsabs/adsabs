'''
Created on Mar 13, 2014

@author: ehenneken
'''
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate, Spacer, Image, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.enums import TA_JUSTIFY
import math
from datetime import datetime
 
########################################################################
class MetricsReport(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.width, self.height = letter
        self.styles = getSampleStyleSheet()
 
    #----------------------------------------------------------------------
    def coord(self, x, y, unit=1):
        """

        http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab

        Helper class to help position flowables in Canvas objects
        """
        x, y = x * unit, self.height -  y * unit
        return x, y
 
    #----------------------------------------------------------------------
    def run(self):
        """
        Run the report
        """
        self.doc = SimpleDocTemplate(self.file_name)
        self.story = [Spacer(1, 2.5*inch)]
        # Different elements are constructed and if successful, they will be added to the 'story'
        # 1. Construct a table with numerical data
        try:
            self.createTables()
        except:
            pass
        # 2. Construct the publication histogram (number of papers per publication year)
        try:
            if not self.single_record:
                self.createPaperHistogram()
        except:
            pass
        # 3. Construct a reads histogram (number of reads per access year)
        try:
            self.createReadsHistogram()
        except:
            pass
        # 4. Construct a citation histogram (number of citations per publication year)
        try:
            self.createCitationHistogram()
        except:
            pass
        # 5. Time series for various indicators
        try:
            self.createTimeSeries('h')
        except:
            pass
        try:
            self.createTimeSeries('g')
        except:
            pass
        try:
            self.createTimeSeries('i10')
        except:
            pass
        try:
            self.createTimeSeries('i100')
        except:
            pass
        try:
            self.createTimeSeries('tori')
        except:
            pass
        try:
            self.createTimeSeries('Read10')
        except:
            pass
        # 6. A page with explanatory text of terms used in the report
        try:
            self.createHelpText()
        except:
            pass
        # Build the actual report
        self.doc.build(self.story, onFirstPage=self.createDocument)
    #----------------------------------------------------------------------
    def createDocument(self, canvas, doc):
        """
        Create the document
        """
        self.c = canvas
        normal = self.styles["Normal"]
        # Include a logo on the report
        logo = Image("adsabs/modules/bibutils/static/img/adslogo_labs.jpg", 100, 48)
        data = [[logo]]
        table = Table(data, colWidths=4*inch)
        table.setStyle([("VALIGN", (0,0), (0,0), "TOP")])
        table.wrapOn(self.c, self.width, self.height)
        table.drawOn(self.c, *self.coord(97, 15, mm))
        # Add some text on the first page
        header_text = "<b>ADS Metrics Report</b>"
        p = Paragraph(header_text, normal)
        p.wrapOn(self.c, self.width, self.height)
        p.drawOn(self.c, *self.coord(100, 18, mm))
        # If the report name is defined (e.g. for metrics based on a query), include this name.
        # Otherwise (e.g. when metrics are based on just a set of bibcodes) only display the
        # creation date
        if self.report_name:
            ptext = "Report name: %s<br/>Creation time: %s" % (self.report_name, self.report_date)
        else:
            ptext = "Creation time: %s" % self.report_date
        p = Paragraph(ptext, style=normal)
        p.wrapOn(self.c, self.width-50, self.height)
        p.drawOn(self.c, 30, 700)
        # A bit of explanatory text to introduce the metrics report
        ptext = """
        This report lists basic and derived statistical indicators for the set of
        publications submitted to this utility. The accuracy of citation indicators is
        limited by the completeness of the ADS citation records. Usage data (reads and downloads)
        is not available prior to 1996, and is a measure for usage through the ADS only 
        (i.e. not through arXiv).
        """
        p = Paragraph(ptext, style=normal)
        p.wrapOn(self.c, self.width-50, self.height)
        p.drawOn(self.c, 30, 650)
    #----------------------------------------------------------------------
    def createTables(self):
        '''
        Routine to create tabular data
        '''
        # We create tables for these quantities
        if self.single_record:
            paper_items = []
            reads_items = ['Total number of reads','Total number of downloads']
            citation_items = ['Total citations','Normalized citations','Refereed citations']
            indicator_items = []
        else:
            paper_items = ['Number of papers','Normalized paper count']
            reads_items = ['Total number of reads','Average number of reads','Median number of reads','Total number of downloads','Average number of downloads','Median number of downloads']
            citation_items = ['Number of citing papers','Total citations','Average citations','Median citations','Normalized citations','Refereed citations','Average refereed citations','Median refereed citations','Normalized refereed citations']
            indicator_items = ['H-index', 'g-index', 'i10-index', 'i100-index', 'tori index', 'roq index', 'read10 index']
        # This dictionary says whether a quantity is an integer (0) or a float (>0)
        paper_prec = {'Number of papers':0,'Normalized paper count':1}
        reads_prec = {'Total number of reads':0,'Average number of reads':1,'Median number of reads':0,'Total number of downloads':0,'Average number of downloads':1,'Median number of downloads':0}
        citation_prec = {'Number of citing papers':0,'Total citations':0,'Average citations':1,'Median citations':0,'Normalized citations':1,'Refereed citations':0,'Average refereed citations':1,'Median refereed citations':0,'Normalized refereed citations':1}
        indicator_prec = {'H-index':0, 'g-index':0, 'i10-index':0, 'i100-index':0, 'tori index':1, 'roq index':1, 'read10 index':0}
        # This dictionary defines the display strings for the various indicators
        indicator_names = {'H-index':'h', 'g-index':'g','i10-index':'i10','i100-index':'i100','tori index':'tori','roq index':'riq','read10 index':'READ10'}
        # Build the table contents
        if self.single_record:
            data = [['Usage','']]
        else:
            data = [['Papers','Total','Refereed']]
        for item in paper_items:
            entry = [item]
            if paper_prec[item] > 0:
                entry.append("%.1f" %self.data['all stats'][item])
                entry.append("%.1f" %self.data['refereed stats'][item])
            else:
                entry.append(int(self.data['all stats'][item]))
                entry.append(int(self.data['refereed stats'][item]))
            data.append(entry)
        for item in reads_items:
            entry = [item]
            if reads_prec[item] > 0:
                entry.append("%.1f" %self.data['all reads'][item])
                if not self.single_record:
                    entry.append("%.1f" %self.data['refereed reads'][item])
            else:
                entry.append(int(self.data['all reads'][item]))
                if not self.single_record:
                    entry.append(int(self.data['refereed reads'][item]))
            data.append(entry)
        if self.single_record:
            data.append(['Citations',''])
        else:
            data.append(['Citations','Total','Refereed'])
        for item in citation_items:
            entry = [item]
            if citation_prec[item] > 0:
                entry.append("%.1f" %self.data['all stats'][item])
                if not self.single_record:
                    entry.append("%.1f" %self.data['refereed stats'][item])
            else:
                entry.append(int(self.data['all stats'][item]))
                if not self.single_record:
                    entry.append(int(self.data['refereed stats'][item]))
            data.append(entry)
        if not self.single_record:
            data.append(['Indicators','Total','Refereed'])
        for item in indicator_items:
            entry = ["%s index" % indicator_names.get(item,item)]
            if indicator_prec[item] > 0:
                entry.append("%.1f" %self.data['all stats'][item])
                entry.append("%.1f" %self.data['refereed stats'][item])
            else:
                entry.append(int(self.data['all stats'][item]))
                entry.append(int(self.data['refereed stats'][item]))
            data.append(entry)
        # Table formatting
        # The 'section' integers define which cells need to be given a background color
        paper_section = len(paper_items) + len(reads_items) + 1
        indicator_section = paper_section + len(indicator_items) + 3
        table = Table(data, colWidths=[200, 80, 80])
        # Color the background of those cells that are header cells
        if not self.single_record:
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(2,0),colors.grey),
                                    ('BACKGROUND',(0,paper_section),(2,paper_section),colors.grey),
                                    ('BACKGROUND',(0,indicator_section),(2,indicator_section),colors.grey)]),
                                    )
        else:
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(2,0),colors.grey),
                                    ('BACKGROUND',(0,paper_section),(2,paper_section),colors.grey)]))
        # Add the table to the 'story'
        self.story.append(table)
        self.story.append(Spacer(1, 12))
 
    #----------------------------------------------------------------------
    def createPaperHistogram(self):
        '''
        Routine to create histogram of numbers of papers published for given years
        '''
        # The vertical bar chart will get added to the 'drawing' object
        drawing = Drawing(400, 200)
        # Now we can start constructing the vertical bar chart
        lc = VerticalBarChart()
        lc.x = 30
        lc.y = 50
        lc.height = 125
        lc.width = 350
        # Record the years, because these values will be used as x axis labels
        years = sorted(map(lambda b: int(b), filter(lambda a: a.isdigit(), self.data['paper histogram'].keys())))
        # This list will hold the data points for the histogram
        lc.data = []
        # Record the counts of both refereed and non-refereed papers
        refereed = []
        non_refereed = []
        # The maximum number of papers will be used to scale the y axis
        max_papers = 0
        # Take only the first two values of each value string in the histogram data
        # The first value is total papers, the second is the number of refereed papers
        for year in years:
            values = map(lambda a: int(a),self.data['paper histogram'][str(year)].split(':')[:2])
            max_papers = max(max_papers, max(values))
            refereed.append(values[1])
            non_refereed.append(values[0]-values[1])
        lc.data.append(refereed)
        lc.data.append(non_refereed)
        # Proper label placement for years: shift by (-6, -6) in x and y to have labels positioned properly
        lc.categoryAxis.labels.dx = -6
        lc.categoryAxis.labels.dy = -6
        # and rotate the labels by 90 degrees
        lc.categoryAxis.labels.angle = 90
        # The label names are the publication years
        lc.categoryAxis.categoryNames = map(lambda a: str(a), years)
        # Define the value step and maximum for the y axis
        lc.valueAxis.valueStep = max(int(math.floor(float(max_papers)/10.0)),1)
        lc.valueAxis.valueMax = int(math.ceil(float(max_papers)/10.0))*10
        lc.valueAxis.valueMin = 0
        # Now add the histogram to the 'drawing' object
        drawing.add(lc)
        # Add a legend to the histogram so that we now which color means what
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 380
        legend.y = 160
        legend.deltax = 60
        legend.dxTextSpace = 10
        items = [(colors.red, 'refereed'), (colors.green, 'non-refereed')]
        legend.colorNamePairs = items
        drawing.add(legend, 'legend')
        # Finally add a title to the histogram
        drawing.add(String(200,190,"publication histogram", textAnchor="middle", fillColor='blue'))
        # Append the result to the 'story'
        self.story.append(drawing) 
    #----------------------------------------------------------------------
    def createReadsHistogram(self):
        '''
        Routine to create histogram of numbers of 'reads' for given years
        '''
        # The vertical bar chart will get added to the 'drawing' object
        drawing = Drawing(400, 200)
        # Now we can start constructing the vertical bar chart
        lc = VerticalBarChart()
        lc.x = 30
        lc.y = 50
        lc.height = 125
        lc.width = 350
        # Record the years, because these values will be used as x axis labels
        years = sorted(map(lambda b: int(b), filter(lambda a: a.isdigit(), self.data['reads histogram'].keys())))
        # This list will hold the data points for the histogram
        lc.data = []
        # Record the counts of both reads of refereed and non-refereed papers
        refereed = []
        non_refereed = []
        # The maximum number of reads will be used to scale the y axis
        max_reads = 0
        # Take only the first two values of each value string in the histogram data
        # The first is for 'all' papers, the second for the 'refereed' papers
        for year in years:
            values = map(lambda a: int(a),self.data['reads histogram'][str(year)].split(':')[:2])
            max_reads = max(max_reads,max(values))
            refereed.append(values[1])
            non_refereed.append(values[0]-values[1])
        lc.data.append(refereed)
        lc.data.append(non_refereed)
        # Proper label placement for years: shift by (-6, -6) in x and y to have labels positioned properly
        lc.categoryAxis.labels.dx = -6
        lc.categoryAxis.labels.dy = -6
        # and rotate the labels by 90 degrees
        lc.categoryAxis.labels.angle = 90
        # Define the value step and maximum for the y axis
        lc.valueAxis.valueMax = int(math.ceil(float(max_reads)/10.0))*10
        lc.valueAxis.valueStep = max(int(math.floor(float(max_reads)/10.0)),1)
        lc.valueAxis.valueMin = 0
        # The label names are the access years
        lc.categoryAxis.categoryNames = map(lambda a: str(a), years)
        # Now add the histogram to the 'drawing' object
        drawing.add(lc)
        # Add a legend to the histogram so that we now which color means what
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 380
        legend.y = 160
        legend.deltax = 60
        legend.dxTextSpace = 10
        items = [(colors.red, 'refereed'), (colors.green, 'non-refereed')]
        legend.colorNamePairs = items
        drawing.add(legend, 'legend')
        # Finally add a title to the histogram
        drawing.add(String(200,190,"reads histogram", textAnchor="middle", fillColor='blue'))
        # Append the result to the 'story'
        self.story.append(drawing)
    #----------------------------------------------------------------------
    def createCitationHistogram(self):
        '''
        Routine to create a histogram of citations:
        1. refereed papers to refereed papers
        2. refereed papers to non-refereed papers
        3. non-refereed papers to refereed papers
        4. non-refereed papers to non-refereed papers
        (where 'to X' means 'to the papers of type X in the publication set, used to generate the metrics)
        '''
        # The vertical bar chart will get added to the 'drawing' object
        drawing = Drawing(400, 200)
        # Now we can start constructing the vertical bar chart
        lc = VerticalBarChart()
        lc.x = 30
        lc.y = 50
        lc.height = 125
        lc.width = 350
        # Record the publication years, because these values will be used as x axis labels
        years = sorted(map(lambda b: int(b), filter(lambda a: a.isdigit(), self.data['citation histogram'].keys())))
        # This list will hold the data points for the histogram
        lc.data = []
        # Record the counts for the 4 different types of citations
        ref_ref = []
        ref_non = []
        non_ref = []
        non_non = []
        # The maximum number of citations will be used to scale the y axis
        max_citations = 0
        # Take only the first four values of each value string in the histogram data
        for year in years:
            values = map(lambda a: int(a),self.data['citation histogram'][str(year)].split(':')[:4])
            all2all = values[0]
            all2ref = values[2]
            ref2ref = values[3]
            ref2all = values[1]
            all2non = all2all - all2ref
            ref2non = ref2all - ref2ref
            non2all = all2all - ref2all
            non2ref = all2ref - ref2ref
            non2non = non2all - non2ref
            ref_ref.append(ref2ref)
            ref_non.append(ref2non)
            non_ref.append(non2ref)
            non_non.append(non2non)
            max_citations = max(max_citations,ref2ref,ref2non,non2ref,non2non)
        lc.data.append(ref_ref)
        lc.data.append(ref_non)
        lc.data.append(non_ref)
        lc.data.append(non_non)
        # If there are no citations, just omit this histogram:
        if max_citations == 0:
            return
        # Proper label placement for years: shift by (-6, -6) in x and y to have labels positioned properly
        lc.categoryAxis.labels.dx = -6
        lc.categoryAxis.labels.dy = -6
        # and rotate the labels by 90 degrees
        lc.categoryAxis.labels.angle = 90
        # The label names are the publication years
        lc.categoryAxis.categoryNames = map(lambda a: str(a), years)
        # Define the colors for the various bars
        lc.bars[0].fillColor = colors.red
        lc.bars[1].fillColor = colors.green
        lc.bars[2].fillColor = colors.blue
        lc.bars[3].fillColor = colors.orange
        # Define the value step and maximum for the y axis
        lc.valueAxis.valueMax = int(math.ceil(float(max_citations)/10.0))*10
        lc.valueAxis.valueStep = max(int(math.floor(float(max_citations)/10.0)),1)
        # Now add the histogram to the 'drawing' object
        drawing.add(lc)
        # Add a legend to the histogram so that we now which color means what
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 380
        legend.y = 160
        legend.deltax = 60
        legend.dxTextSpace = 10
        legend.columnMaximum = 6
        items = [(colors.red, 'refereed to refereed'), (colors.green, 'refereed to non-refereed'),(colors.blue, 'non-refereed to refereed'),(colors.orange, 'non-refereed to non-refereed')]
        legend.colorNamePairs = items
        drawing.add(legend, 'legend')
        # Finally add a title to the histogram
        drawing.add(String(200,190,"citation histogram", textAnchor="middle", fillColor='blue'))
        # Append the result to the 'story'
        self.story.append(drawing)
    #----------------------------------------------------------------------
    def createTimeSeries(self,ser):
        if self.single_record:
            return
        # Time series are available for these quantities. The number indicates their position in the data string
        series = {'h':0, 'g':1, 'i10':2, 'i100':6, 'tori':3, 'Read10':7}
        # The time series plot will get added to the 'drawing' object
        drawing = Drawing(400, 200)
        # and it is of type 'LinePlot'
        lp = LinePlot()
        lp.x = 30
        lp.y = 50
        lp.height = 125
        lp.width = 350
        # Record the publication years, because these values will be used as x axis labels
        years = sorted(map(lambda b: int(b), filter(lambda a: a.isdigit(), self.data['metrics series'].keys())))
        lp.data = []
        series_data = []
        # The maximum value will be used to scale the y axis
        max_value = 0
        # This list will hold the data points for the histogram
        for year in years:
            values = map(lambda a: float(a),self.data['metrics series'][str(year)].split(':'))
            max_value = max(max_value,values[series[ser]])
            if ser == 'read10' and year > 1995:
                series_data.append((year,values[series[ser]]))
            else:
                series_data.append((year,values[series[ser]]))

        lp.data.append(series_data)
        lp.joinedLines = 1
        # Define the line color
        lp.lines[0].strokeColor = colors.orange
        # Actual data point will be marked by a filled circle
        lp.lines.symbol = makeMarker('FilledCircle')
        lp.strokeColor = colors.black
        # The extreme values for the x axis
        lp.xValueAxis.valueMin = years[0]
        lp.xValueAxis.valueMax = years[-1]
        # Proper label placement for years: shift by (-6, -6) in x and y to have labels positioned properly
        lp.xValueAxis.labels.dx = -6
        lp.xValueAxis.labels.dy = -18
        # and rotate the labels by 90 degrees
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.valueSteps = years
        # For both axes values will be displayed as integers
        lp.xValueAxis.labelTextFormat = '%2.0f'
        lp.yValueAxis.labelTextFormat = '%2.0f'
        # Define the maximum value of the y axis
        lp.yValueAxis.valueMax = int(math.ceil(float(max_value)/10.0))*10
        # Depending on the range of values, set a value step for the y axis
        if max_value > 10000:
            lp.yValueAxis.valueStep = 1000
        elif max_value > 1000:
            lp.yValueAxis.valueStep = 100
        else:
            lp.yValueAxis.valueStep = 10
        # The y axis always starts at 0
        lp.yValueAxis.valueMin = 0
        # Now add the line plot to the 'drawing' object
        drawing.add(lp)
        # Finally add the appropriate title to the plot
        drawing.add(String(200,190,"%s index time series" % ser, textAnchor="middle", fillColor='blue'))
        # Append the result to the 'story'
        self.story.append(drawing)
    #----------------------------------------------------------------------
    def createHelpText(self):
        '''
        The last page of the report with text explaining what everything means
        '''
        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        ptext = 'Explanation of terms used in metrics report'
        self.story.append(PageBreak())
        self.story.append(Paragraph(ptext, styles["Normal"]))
        self.story.append(Spacer(1, 12))
        ptext = '''<b>Citations:</b> citation counts are beased on those references that have been matched with existing ADS records. 
                    Refereed citations are citations from refereed publications. The number of citing papers is the number of unique
                    papers citing the papers used for the metrics report.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))    
        ptext = '<b>Reads/downloads:</b> usage statistics have been maintained since 1996. '
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
        ptext = '<b>Normalized quantities:</b> quantities normalized by the number of authors in the publications'
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))    
        ptext = '''<b>Reads/downloads:</b> usage statistics have been maintained since 1996. Reads refer to access of basic metadata
                of publications, while downloads refer to access of fulltext via any of the fulltext links. Usage via arXiv is not
                included in these statistics.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))
        self.story.append(Spacer(1, 12))
        ptext = '''<b>h index:</b> the Hirsch index (h) is the largest number N such that H publications have at least N citations'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
        ptext = '''<b>g index:</b> given a set of articles ranked in decreasing order of the number of citations that they received, 
                   the g-index is the (unique) largest number such that the top g articles received (together) at least g<sup>2</sup> 
                   citations.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12)) 
        ptext = '''<b>i<sub>N</sub> index:</b> the i<sub>N</sub> index is the number of publications with at least N citations.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
        ptext = '''<b>tori index:</b> the tori index is calculated using the reference lists of the citing papers, where self-citations are removed. 
                   The contribution of each citing paper is then normalized by the number of remaining references in the citing papers 
                   and the number of authors in the cited paper.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
        ptext = '''<b>riq index:</b> the riq-index equals the square root of the tori index, divided by the time between the first and last publication.
                The values displayed are the riq index multplied by a factor of 1,000.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
        ptext = '''<b>Read10 index:</b> Read10 is the current readership rate for those papers in the set published in the most recent ten years, 
                   normalized for number of authors.'''
        self.story.append(Paragraph(ptext, styles["Normal"]))   
        self.story.append(Spacer(1, 12))
