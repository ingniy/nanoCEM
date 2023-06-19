# Current_Magnifier
`Current_Magnifier` is a sample tool designed to visualize the features(Mean,Median,Dwell_time,STD) that distinguish between two groups of ONT data from the same species at the site level.
It supports two re-squiggle pipeline(`Tombo` and `f5c`). From R9 to R10, Tombo/nanopolish/f5c applied different method to optimise the alignment. So, this program can examine the differences in the current generated by ONT at the same site across multiple dimensions, making it easier for researchers to showcase and demonstrate their discoveries of mutations and modifications.
If you want to view single read signal or raw signal, [Squigualiser](https://github.com/hiruna72/squigualiser) is recommended.

## Example
Here is an example that show the difference of A2030 on 23S rRNA.
![alt text](example/boxplot.png)
![alt text](example/violin.png)

## Before start, you should know
### What is re-squiggle
In ONT technology, "resquiggle" refers to the process of converting the raw electrical signals from the sequencer into corresponding DNA/RNA sequence information, which is then corrected and realigned. 
This process utilizes the signal features of ONT sequencing, such as changes in electrical resistance and noisy signals, to capture information from the DNA/RNA sequence and analyze and interpret it. 
Although new basecaller program (Guppy/Boinito/Dorado) generated the bam file with move table to record the event index,but  resquiggle is a more fine alignment than the move table in most cases.
### Data format
Since the release of the R10, ONT's data formats have become more diverse, including the initial fast5 format, the new pod5 format, and community-provided slow5/blow5 formats. The relationship between them and conversion tools are shown in the following figure.
![alt text](example/data_format.png)

In our program, we assume that the input provided by the user is in the **multi-fast5** format by default.
### Reference and alignment
For RNA showcase, the expected input for the vast majority of species is a fasta file of transcripts, rather than the genome. This is because RNA undergoes splicing and other phenomena after transcription, allowing a single gene to produce multiple different transcripts with varying splicing forms and exon compositions.

## Installation
Requirement : Python >=3.7, <3.10

```sh
pip install current_events_magnifier==0.0.3.8
pip install ont-fast5-api
conda install -c bioconda ont_vbz_hdf_plugin f5c slow5tools
```
## Options
### read_tombo_resquiggle
```sh
CE_magnifier.py tombo -h
optional arguments:
  -h, --help            show this help message and exit
  --basecall_group BASECALL_GROUP
                        The attribute group to extract the training data from. e.g. RawGenomeCorrected_000
  --basecall_subgroup BASECALL_SUBGROUP
                        Basecall subgroup Nanoraw resquiggle into. Default is BaseCalled_template
  -i FAST5, --fast5 FAST5
                        fast5_file
  -c CONTROL_FAST5, --control_fast5 CONTROL_FAST5
                        control_fast5_file
  -o OUTPUT, --output OUTPUT
                        output_file
  --chrom CHROM         Gene or chromosome name(head of your fasta file)
  --pos POS             site of your interest
  --len LEN             region around the position (default:10)
  --strand STRAND       Strand of your interest (default:+)
  -t CPU, --cpu CPU     num of process (default:8)
  --ref REF             fasta file
  --overplot-number OVERPLOT_NUMBER (default:500)
                        Number of read will be used to plot
```
### read_f5c_resquiggle
```sh
CE_magnifier.py f5c -h
optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path and suffix of blow5, bam file and paf files
  -c CONTROL, --control CONTROL
                        control path and suffix of blow5, bam file and paf files
  -o OUTPUT, --output OUTPUT
                        output_file
  --chrom CHROM         Gene or chromosome name(head of your fasta file)
  --pos POS             site of your interest
  --len LEN             region around the position (default:10)
  --strand STRAND       Strand of your interest (default:+)
  --ref REF             fasta file
  --overplot-number OVERPLOT_NUMBER (default:500)
                        Number of read will be used to plot

```
## Quick start
### Run Basecaller on your ONT data
```sh
# assumed your fast5 file folder name is fast5/
guppy_basecaller -i fast5/ -s ./guppy_out --recursive --device auto -c rna_r9.4.1_70bps_hac.cfg  &
cat guppy_out/*/*.fastq > all.fastq
```
Option ```-c``` means config file ,which will depend on your data
### Decide the chrom or transcript name and region of your interest
In this sample, I plot the 23s rRNA whose header in fasta file is NR_103073.1 and I am intereted in A2030 on the plus strand.
So for the following command , I used ```--chrom NR_103073.1  --pos 2030 --strand +```.
### 1. F5c resquiggle (v1.2) (support R10)
Step 1 and 2 should run on your two sample respectively, before the step 3.
1. Data format conversion.
```sh
slow5tools f2s fast5/ -d blow5_dir
slow5tools merge blow5_dir -o file.blow5
slow5tools index file.blow5
```
2. Run f5c resquiggle
```sh
minimap2 -ax map-ont -t 16 --MD reference.fasta all.fastq | samtools view -hbS -F 260 - | samtools sort -@ 6 -o file.bam
samtools index file.bam
f5c resquiggle -c final.fastq file.blow5 -o file.paf
```
3. Run current_events_magnifier to plot
```sh
# run the pipeline below for your two sample respective and keep the suffix of bam/paf/blow5 is the same
python CE_magnifier.py f5c -i sample1/file -c sample2/file -o f5c_result \
--chrom NR_103073.1 --strand + \
--pos 3929 --len 10 \
--ref reference.fasta 
```
### 2. Tombo resquiggle (v1.5.0)
Step 1 and 3 should run on your two sample respectively, before the step 4.
1. Data format conversion.
```sh
# assumed your fast5 file folder name is fast5/
multi_to_single_fast5 -i fast5/ -s single/ --recursive -t 16
```
2. Subsample (Optional)

Because Tombo resquiggle runs very slowly, it heavily relies on the read and write speed of SSD hard drives. Therefore, it is recommended to extract the aligned reads in advance.
After obtaining the single-format fast5 files and bam files , we provide a script that can assist you with this.
```sh
minimap2 -ax map-ont -t 16 --MD reference.fasta all.fastq | samtools view -hbS -F 260 - | samtools sort -@ 6 -o file.bam
samtools index file.bam
extract_sub_fast5_from_bam.py -i single/ -o subsample_single/ -b file.bam --chrom NR_103073.1 --pos 2030 
```
3. Run tombo resquiggle
```sh
# if fast5 is not single format need to transfer to single format by ont-fast-api
# single is fast5s-base-directory

tombo preprocess annotate_raw_with_fastqs --fast5-basedir  single/ --fastq-filenames all.fastq --processes 16 
tombo resquiggle single/ reference.fasta --processes 16 --num-most-common-errors 5
# Notes:
# Tombo resquiggle will take various of time, which means subsample your aligned reads of the special region is recommended
# Run the Tombo pipeline above for your two sample respective, the SSD disk is recommended 
# If you ran step2, run the tombo command on subsample_single but single
```
4. Run current_events_magnifier to plot
```sh
python CE_magnifier.py tombo -i sample1/single -c sample2/single -o tombo_result --chrom NR_103073.1 --strand + --pos 2030 --len 5 --cpu 4 --ref reference.fasta
```





