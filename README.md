# RefSeq Data Download Script

This repository contains a script to download RefSeq CDS and GFF files using NCBI datasets for any family, focusing on chromosome-level assemblies.

## Files

- `download_refseq_cds_gff.py` - Main Python script for downloading RefSeq data
- `README_refseq_download.md` - This documentation file

## Prerequisites

1. **NCBI datasets tool**: The script expects the NCBI datasets tool to be available at `/home5/ibirchl/Bioinformatics_tools/datasets`
2. **Python 3**: The script requires Python 3 with standard libraries
3. **Internet connection**: For downloading data from NCBI

## Usage

### Basic Usage

```bash
# Download CDS and GFF files for gobiidae (goby family)
python3 download_refseq_cds_gff.py --family gobiidae

# Download CDS and GFF files for apogonidae (cardinal fish family)
python3 download_refseq_cds_gff.py --family apogonidae

# Download CDS and GFF files for salmonidae (salmon family)
python3 download_refseq_cds_gff.py --family salmonidae
```

### Advanced Options

```bash
# Download to a custom directory
python3 download_refseq_cds_gff.py --family gobiidae --output-dir my_refseq_data

# Download only CDS files
python3 download_refseq_cds_gff.py --family gobiidae --no-gff

# Download only GFF files
python3 download_refseq_cds_gff.py --family gobiidae --no-cds

# Use a different NCBI datasets tool path
python3 download_refseq_cds_gff.py --family gobiidae --datasets-tool /path/to/datasets

# Show help
python3 download_refseq_cds_gff.py --help
```

## Output Structure

The script creates the following directory structure:

```
refseq_data/
├── cds_files/          # CDS sequence files (RefSeq format)
│   ├── GCF_009829125.3_gobiidae.fna
│   ├── GCF_902148855.1_apogonidae.fna
│   └── ...
└── gff_files/          # GFF annotation files (RefSeq format)
    ├── GCF_009829125.3_gobiidae.gff
    ├── GCF_902148855.1_apogonidae.gff
    └── ...
```

## Key Features

- **Chromosome-level assemblies only**: Focuses on high-quality genome assemblies
- **Any family support**: Can download data for any taxonomic family
- **RefSeq format**: Downloads data from NCBI RefSeq database
- **Automatic file organization**: Files are automatically organized by type and family
- **Error handling**: Robust error handling and logging
- **Progress tracking**: Shows progress for each family being processed
- **Cleanup**: Automatically removes temporary files and zip archives

## Assembly Level Filtering

The script specifically filters for chromosome-level assemblies using the `--assembly-level chromosome` parameter. This ensures:

- Higher quality genome assemblies
- Better gene annotation quality
- More complete genome coverage
- Reduced fragmentation compared to scaffold or contig-level assemblies

## File Formats

### CDS Files
- **Format**: FASTA (.fna)
- **Content**: Coding sequences from genomic DNA
- **Naming**: `{accession}_{family}.fna`
- **Source**: `cds_from_genomic.fna` files from RefSeq

### GFF Files
- **Format**: GFF3 (.gff)
- **Content**: Gene annotations and features
- **Naming**: `{accession}_{family}.gff`
- **Source**: GFF annotation files from RefSeq

## Example Families

Here are some example families you can download:

- **gobiidae**: Gobies and mudskippers
- **apogonidae**: Cardinal fishes
- **salmonidae**: Salmon and trout
- **cyprinidae**: Carps and minnows
- **cichlidae**: Cichlids
- **tetraodontidae**: Pufferfishes
- **gadidae**: Cod and related fishes
- **pleuronectidae**: Flatfishes

## Troubleshooting

### Common Issues

1. **NCBI datasets tool not found**
   - Ensure the tool is installed at `/home5/ibirchl/Bioinformatics_tools/datasets`
   - Or specify a different path using `--datasets-tool`

2. **Permission denied**
   - Make sure the script is executable: `chmod +x download_refseq_cds_gff.py`

3. **No species found**
   - Check your internet connection
   - Verify the family name is correct (use lowercase)
   - The family may not have chromosome-level assemblies available

4. **Large downloads**
   - Chromosome-level assemblies can be large (hundreds of MB to GB)
   - Ensure you have sufficient disk space
   - Downloads may take time depending on your internet connection

### Logging

The script provides detailed logging output. If you encounter issues, check the log messages for specific error information.

## Example Output

```
2024-01-15 10:30:00 - INFO - NCBI datasets tool version: v16.0.0
2024-01-15 10:30:01 - INFO - Searching for available gobiidae species with chromosome-level assemblies...
2024-01-15 10:30:02 - INFO - Found 4 gobiidae genomes with chromosome-level assemblies and CDS/GFF annotations
2024-01-15 10:30:03 - INFO - Found 1 gobiidae taxa with chromosome-level assemblies
2024-01-15 10:30:04 - INFO - Processing gobiidae...
2024-01-15 10:30:05 - INFO - Downloading genome data for gobiidae (chromosome-level assemblies only)...
2024-01-15 10:30:06 - INFO - Running command: /home5/ibirchl/Bioinformatics_tools/datasets download genome taxon gobiidae --include cds,gff3 --assembly-level chromosome --filename refseq_gobiidae_chromosome_data.zip
2024-01-15 10:30:10 - INFO - Download completed for gobiidae
2024-01-15 10:30:11 - INFO - Extracting and organizing files from refseq_gobiidae_chromosome_data.zip...
2024-01-15 10:30:12 - INFO - Moved CDS file: GCF_009829125.3_gobiidae.fna
2024-01-15 10:30:13 - INFO - Moved GFF file: GCF_009829125.3_gobiidae.gff
2024-01-15 10:30:14 - INFO - Successfully processed gobiidae
2024-01-15 10:30:15 - INFO - Successfully processed 1/1 taxa
2024-01-15 10:30:16 - INFO - Download process completed successfully!
2024-01-15 10:30:16 - INFO - CDS files saved to: refseq_data/cds_files
2024-01-15 10:30:16 - INFO - GFF files saved to: refseq_data/gff_files
```

## Comparison with Other Scripts

This script differs from the original goby download script in several ways:

| Feature | Original Script | RefSeq Script |
|---------|----------------|---------------|
| **Scope** | Specific to gobies | Any family |
| **Assembly Level** | All levels | Chromosome only |
| **Database** | General NCBI | RefSeq only |
| **File Formats** | Mixed formats | RefSeq-specific |
| **Usage** | `--species` or `--all` | `--family` |

## License

This script is provided as-is for research purposes. Please ensure you comply with NCBI's terms of service when downloading data.

