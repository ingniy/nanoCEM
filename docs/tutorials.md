# ![logo](logo_tiny.png "nanoCEM")Quick start

This quick start guide outlines the steps to use the nanoCEM command line for analyzing our example data, which consists
of the E. coli 23S rRNA around a known m6A site (A2030). nanoCEM will calculate alignment features and current event
features within this target region.

 **Notes:** Our default mode is `f5c`, so our framework integrated the `f5c` commands. 
 However, for `tombo`, although we have added support for it, you will need to set up the additional `tombo` environment 
 and run tombo resquiggle command . If you want to deal with DNA data, remember to delete all `--rna` in the following commands. 
 For script `current_event_magnifier`, to use the `r10` mode instead of the default `r9` mode, you can use the command `--pore r10`
## Dataprep

[comment]: <> (Before utilizing NanoCEM, it is required to convert the raw data format to the appropriate format &#40;single-format `fast5`)

[comment]: <> (or `blow5`&#41; and perform basecalling to obtain a `fastq` file. Subsequently, select a suitable reference `fasta` file)

[comment]: <> (based on research requirements and proceed with the re-squiggle process using either `tombo` or `f5c`.)
Before utilizing nanoCEM, it is required to convert the raw data format to the appropriate format `blow5` and 
perform basecalling to obtain a `fastq` file. Subsequently, select a suitable reference `fasta` file.
The current ONT default output is the `pod5` format, here is a script to transfer,
    
    # install package
    pip install blue-crab

    # blow5 to blow5
    blue-crab p2s file.pod5 -o file.blow5

For more details and commands, please refer to the [Data preparation from raw reads](preparation.md) page.

## Download the example data

    git clone https://github.com/lrslab/nanoCEM
    cd nanoCEM/example

The path to the downloaded data is as follows:

    data/
        wt/
            file.blow5  # blow5 file for f5c re-squiggle
            file.fastq # basecall result file
        ivt/
            file.blow5  # blow5 file for f5c re-squiggle
            file.fastq # basecall result file
        23S_rRNA.fasta  # reference fasta file
        ...     

## Alignment feature visualization

To compare two groups' alignment feature,  their `fastq` files , reference file and the target position are required.Here is a
script using our test data to visualize the alignment feature,

    # get alignment visualization 
    alignment_magnifier -i data/wt/file.fastq  -c data/ivt/file.fastq  \
    --chrom NR_103073.1 --pos 2030 --len 10 --strand + \
    --rna --ref data/23S_rRNA.fasta --output nanoCEM_result 

Then nanoCEM will output the alignment feature table called [`alignment_feature.csv`](output_format.md) and figure in
your target region as below, `Sample` is from `-i` and `Control` is  `-c`

<center>![alignment](Alignment.png "Alignment visualization") </center>

## Current event feature visualization

For the current event feature,  `current_events_magnifier` script is provided to visualize and analyse related feature.
We support `f5c`, please make sure that the prefix of `fastq`, `blow5` should be the same
for each group as below,

    test/
        file.blow5
        file.fastq

Then you can use `current_events_magnifier` as below,

    # run f5c mode
    current_events_magnifier f5c -i data/wt/file -c data/ivt/file \
    --chrom NR_103073.1 --strand + --pos 2030 \
    --ref data/23S_rRNA.fasta -o nanoCEM_result \
    --base_shift 2 --rna --norm

Then nanoCEM will output the current feature called [`current_feature.csv`](output_format.md) of your target region
and plot it as below,

<center>![f5c_feature](Current_boxplot_f5c.png "f5c_feature") </center>

Meanwhile, to visually display the differences in current features of target position (A2030) between two groups, the
3-mer's feature will be collected within each group can be subjected to Principal Component Analysis (PCA).

<center>![f5c_pca](PCA_target_position.png "f5c_pca") </center>

Finally, in order to demonstrate the difference in current between each point in the target region, we utilized MANOVA to analyze 
the results of PCA and determine the presence of statistically significant differences. `MANOVA_result.csv` and the figure below will be saved in the 
output path.

<center>![manova](RNA_pval.png "manova") </center>

## tombo support

In addition to `f5c`, nanoCEM also supports `tombo`, they are different in several aspects, including the re-squiggle algorithm
(which may introduce one base bias) and the supported data types (fast5/blow5). And nanoCEM achieves the same functionality by 
providing the fast5 folder like the following workflow,

### Dataprep

Tombo is a suite of tools primarily for the identification of modified nucleotides from nanopore sequencing data, and only support single-format fast5.

    # pod5 to single-format fast5
    pod5 convert to_fast5 file.pod5 --output </path/to/multi_reads>
    multi_to_single_fast5 --input_path </path/to/multi_reads> --save_path </path/to/single_reads> --recursive

For Sample and Control group,  files should be as below,

    test/
        single/
        file.fastq

###  tombo resquiggle
For Sample and Control group, run the commands below respectively, but for our example data, tombo resquiggle has been done and can **skip** this step
 
    tombo preprocess annotate_raw_with_fastqs --fast5-basedir single/ --fastq-filenames file.fastq --processes 16 
    tombo resquiggle single/ ../23S_rRNA.fasta --processes 16 --num-most-common-errors 5
    
### current_events_magnifier
Afterwards, you can run the `current_event_magnifier` function in the `tombo` mode to achieve the same functionality.

    # run tombo mode
    current_events_magnifier tombo -i data/wt/single -c data/ivt/single \
    --chrom NR_103073.1 --strand + --pos 2030 \
    --ref data/23S_rRNA.fasta -o nanoCEM_result \
    --rna --cpu 4 --norm

Then nanoCEM will output the current feature called [`current_feature.csv`](output_format.md) of your target region