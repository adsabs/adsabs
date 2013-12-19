/**
 * Javascript for the Metrics page
 * Help tooltip manager
 */

var HelpTipManager = new Object();

//help text
HelpTipManager.help_text = new Object();
HelpTipManager.help_text['NUMBER_OF_PAPERS'] = {'title':'Number of papers', 'help':'The total number of papers'};
HelpTipManager.help_text['NORMALIZED_PAPER_COUNT'] = {'title':'Normalized paper count', 'help': 'For a list of N papers (i=1,...N), where N<sub>auth</sub><sup>i</sup> is the number of authors for publication i, the normalized paper count is the sum over 1/N<sub>auth</sub><sup>i</sup>'};
HelpTipManager.help_text['NUMBER_OF_CITING_PAPERS'] = {'title':'Number of citing papers', 'help': 'Number of unique papers citing the papers in the submitted list.'};
HelpTipManager.help_text['TOTAL_CITATIONS'] = {'title':'Total citations', 'help': 'The total number of times all papers in the list were cited.'};
HelpTipManager.help_text['AVERAGE_CITATIONS'] = {'title':'Average citations', 'help': 'The total number of citations divided by the number of papers.'};
HelpTipManager.help_text['MEDIAN_CITATIONS'] = {'title':'Median citations', 'help': 'The median of the citation distribution.'};
HelpTipManager.help_text['NORMALIZED_CITATIONS'] = {'title':'Normalized citations', 'help': 'For a list of N papers (i=1,...N), where N<sub>auth</sub><sup>i</sup> is the number of authors for publication i and C<sub>i</sub> the number of citations that this paper received, the normalized citation count for each article is \
C<sub>i</sub>/N<sub>auth</sub><sup>i</sup> ,and the \'normalized citations\' for this list of N papers is the sum of these N numbers.'};
HelpTipManager.help_text['REFEREED_CITATIONS'] = {'title':'Refereed citations', 'help': 'Number of refereed citing papers.'};
HelpTipManager.help_text['AVERAGE_REFEREED_CITATIONS'] = {'title':'Average refereed citations', 'help': 'The average number of citations from refereed publications to all/refereed publications in the list.'};
HelpTipManager.help_text['MEDIAN_REFEREED_CITATIONS'] = {'title':'Median refereed citations', 'help': 'The average median of citations from refereed publications to all/refereed publications in the list.'};
HelpTipManager.help_text['NORMALIZED_REFEREED_CITATIONS'] = {'title':'Normalized refereed citations', 'help': 'The normalized number of citations from refereed publications to all/refereed publications in the list.'};
HelpTipManager.help_text['TOTAL_NUMBER_OF_READS'] = {'title':'Total number of reads', 'help': 'The total number of times all papers were "read". For each paper, a "read" is counted if an ADS user runs a search in our system and then requests to either view the paper\'s full bibliographic record or download the fulltext.'};
HelpTipManager.help_text['AVERAGE_NUMBER_OF_READS'] = {'title':'Average number of reads', 'help': 'The total number of reads divided by the number of papers.'};
HelpTipManager.help_text['MEDIAN_NUMBER_OF_READS'] = {'title':'Median number of reads', 'help': 'The median of the reads distribution.'};
HelpTipManager.help_text['TOTAL_NUMBER_OF_DOWNLOADS'] = {'title':'Total number of downloads', 'help': 'The total number of times full text (article or e-print) was accessed.'};
HelpTipManager.help_text['AVERAGE_NUMBER_OF_DOWNLOADS'] = {'title':'Average number of downloads', 'help': 'The total number of downloads divided by the number of papers.'};
HelpTipManager.help_text['MEDIAN_NUMBER_OF_DOWNLOADS'] = {'title':'Median number of downloads', 'help': 'The median of the downloads distribution.'};
HelpTipManager.help_text['H_INDEX'] = {'title':'h-index', 'help': 'The H-index is the largest number H such that H publications have at least H citations.'};
HelpTipManager.help_text['G_INDEX'] = {'title':'g-index', 'help': 'Given a set of articles ranked in decreasing order of the number of citations that they received, the g-index is the (unique) largest number such that the top g articles received (together) at least g<sup>2</sup> citations.'};
HelpTipManager.help_text['E_INDEX'] = {'title':'e-index', 'help': 'The e-index is calculated (using a citation-sorted list of publications) as e<sup>2</sup> = &Sigma;<sub>j=1</sub><sup>H</sup>c<sub>j</sub> - H<sup>2</sup> \
where c<sub>j</sub> is the number of citations received by paper j, and it represents the ignored excess citations. It is not a replacement for H, but to be used in conjection with H. In other words, for a citation-ordered list of publications, the square of e equals the sum of citations up to the publication with rank H.'};
HelpTipManager.help_text['I10_INDEX'] = {'title':'i10-index', 'help': 'The i10-index is the number of publications with at least 10 citations.'};
HelpTipManager.help_text['TORI_INDEX'] = {'title':'tori-index', 'help': 'The tori-index is calculated using the reference lists of the citing papers, where self-citations are removed. The contribution of each citing paper is then normalized by the number of remaining references in the citing papers and the number of authors in the cited paper.'};
HelpTipManager.help_text['ROQ_INDEX'] = {'title':'riq-index', 'help': 'The riq-index equals the square root of the tori-index, divided by the time between the first and last publication.'};
HelpTipManager.help_text['M_INDEX'] = {'title':'m-index', 'help': 'The m-index is the h-index divided by the time (years) between the first and most recent publication.'};

// function that shows an help text for the different options of a search page
HelpTipManager.show_help = function(item)
{
    // Get the help text
	var text_type = this.help_text[item.id];
	//I create the QTIP element
	$(item).popover({
	    html: true,
	    trigger: "hover focus",
	    title: text_type['title'],
	    content: text_type['help'],
	});
};