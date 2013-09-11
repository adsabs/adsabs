/**
 * Javascript for the Metrics page
 * Help qtip manager
 */

var QtipManager = new Object();

//help text
QtipManager.help_text = new Object();
QtipManager.help_text['NUMBER_OF_PAPERS'] = '<span style="font-weight: bold;">Number of papers</span><br/><br/>'+
'The number of papers used to calculate the metrics.';
QtipManager.help_text['NORMALIZED_PAPER_COUNT'] = '<span style="font-weight: bold;">Normalized paper count</span><br/><br/>'+
'For a list of N papers (i=1,...N), where N<sub>auth</sub><sup>i</sup> is the number of authors for publication i, \
the normalized paper count is the sum over 1/N<sub>auth</sub><sup>i</sup>';
QtipManager.help_text['NUMBER_OF_CITING_PAPERS'] = '<span style="font-weight: bold;">Number of citing papers</span><br/><br/>'+
'Number of unique papers citing the papers in the submitted list.';
QtipManager.help_text['TOTAL_CITATIONS'] = '<span style="font-weight: bold;">Total citations</span><br/><br/>'+
'The total number of times all papers in the list were cited.';
QtipManager.help_text['AVERAGE_CITATIONS'] = '<span style="font-weight: bold;">Average citations</span><br/><br/>'+
'The total number of citations divided by the number of papers.';
QtipManager.help_text['MEDIAN_CITATIONS'] = '<span style="font-weight: bold;">Median citations</span><br/><br/>'+
'The median of the citation distribution.';
QtipManager.help_text['NORMALIZED_CITATIONS'] = '<span style="font-weight: bold;">Normalized citations</span><br/><br/>'+
'For a list of N papers (i=1,...N), where N<sub>auth</sub><sup>i</sup> is the number of authors for publication i and \
C<sub>i</sub> the number of citations that this paper received, the normalized citation count for each article is \
C<sub>i</sub>/N<sub>auth</sub><sup>i</sup> ,and the \'normalized citations\' for this list of N papers is the sum of these N numbers.';
QtipManager.help_text['REFEREED_CITATIONS'] = '<span style="font-weight: bold;">Refereed citations</span><br/><br/>'+
'Number of refereed citing papers.';
QtipManager.help_text['AVERAGE_REFEREED_CITATIONS'] = '<span style="font-weight: bold;">Average refereed citations</span><br/><br/>'+
'The average number of citations from refereed publications to all/refereed publications in the list.';
QtipManager.help_text['MEDIAN_REFEREED_CITATIONS'] = '<span style="font-weight: bold;">Median refereed citations</span><br/><br/>'+
'The average median of citations from refereed publications to all/refereed publications in the list.';
QtipManager.help_text['NORMALIZED_REFEREED_CITATIONS'] = '<span style="font-weight: bold;">Normalized refereed citations</span><br/><br/>'+
'The normalized number of citations from refereed publications to all/refereed publications in the list.';
QtipManager.help_text['TOTAL_NUMBER_OF_READS'] = '<span style="font-weight: bold;">Total number of reads</span><br/><br/>'+
'The total number of times all papers were "read". For each paper, a "read" is counted if an ADS user runs a search in our system and \
then requests to either view the paper\'s full bibliographic record or download the fulltext.';
QtipManager.help_text['AVERAGE_NUMBER_OF_READS'] = '<span style="font-weight: bold;">Average number of reads</span><br/><br/>'+
'The total number of reads divided by the number of papers.';
QtipManager.help_text['MEDIAN_NUMBER_OF_READS'] = '<span style="font-weight: bold;">Median number of reads</span><br/><br/>'+
'The median of the reads distribution.';
QtipManager.help_text['TOTAL_NUMBER_OF_DOWNLOADS'] = '<span style="font-weight: bold;">Total number of downloads</span><br/><br/>'+
'The total number of times full text (article or e-print) was accessed.';
QtipManager.help_text['AVERAGE_NUMBER_OF_DOWNLOADS'] = '<span style="font-weight: bold;">Average number of downloads</span><br/><br/>'+
'The total number of downloads divided by the number of papers.';
QtipManager.help_text['MEDIAN_NUMBER_OF_DOWNLOADS'] = '<span style="font-weight: bold;">Median number of downloads</span><br/><br/>'+
'The median of the downloads distribution.';
QtipManager.help_text['H_INDEX'] = '<span style="font-weight: bold;">h-index</span><br/><br/>'+
'The H-index is the largest number H such that H publications have at least H citations.';
QtipManager.help_text['G_INDEX'] = '<span style="font-weight: bold;">g-index</span><br/><br/>'+
'Given a set of articles ranked in decreasing order of the number of citations that they received, \
the g-index is the (unique) largest number such that the top g articles received (together) at least \
g<sup>2</sup> citations.';
QtipManager.help_text['E_INDEX'] = '<span style="font-weight: bold;">e-index</span><br/><br/>'+
'The e-index is calculated (using a citation-sorted list of publications) as \
e<sup>2</sup> = &Sigma;<sub>j=1</sub><sup>H</sup>c<sub>j</sub> - H<sup>2</sup> \
where c<sub>j</sub> is the number of citations received by paper j, and it represents the ignored excess citations. \
It is not a replacement for H, but to be used in conjection with H. In other words, for a citation-ordered list of \
publications, the square of e equals the sum of citations up to the publication with rank H.';
QtipManager.help_text['I10_INDEX'] = '<span style="font-weight: bold;">i10-index</span><br/><br/>'+
'The i10-index is the number of publications with at least 10 citations.';
QtipManager.help_text['TORI_INDEX'] = '<span style="font-weight: bold;">tori-index</span><br/><br/>'+
'The tori-index is calculated using the reference lists of the citing papers, where self-citations are removed. \
The contribution of each citing paper is then normalized by the number of remaining references in the \
citing papers and the number of authors in the cited paper.';
QtipManager.help_text['ROQ_INDEX'] = '<span style="font-weight: bold;">riq-index</span><br/><br/>'+
'The riq-index equals the square root of the tori-index, divided by the time between the first and last publication.';
QtipManager.help_text['M_INDEX'] = '<span style="font-weight: bold;">m-index</span><br/><br/>'+
'The m-index is the h-index divided by the time (years) between the first and most recent publication.';



//function that shows an help text for the different options of a search page
QtipManager.show_help = function(item)
{
	var type = (item.id.split('option_'))[1];
	//I extract the text
	var text_type = this.help_text[type];
	//I create the QTIP element
	$(item).qtip({
		content: text_type,
		show: {
			when: 'click',
			ready: true,
			solo: true
		},
		hide: 'click',
		position: {
			corner: {
				target: 'bottomRight',
				tooltip: 'topLeft'
			},
		},
		style: {
			'background-color': '#FFF',
			'font-size': '0.9em',
			padding: '7px 13px',
			width: {
				max: 250,
				min: 150
			},
			tip: true,
			border: {
				width: 3,
				radius: 3,
				color: '#CCF'
			},
		},
	});
};

//Method to hide the contextual help
QtipManager.hide_help = function()
{
	//I remove the current element 
	$('.qtip.qtip-defaults.qtip-active').qtip("destroy");
	//and also the others
	$('.qtip.qtip-defaults').qtip("destroy");
};