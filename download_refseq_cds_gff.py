#!/usr/bin/env python3
"""
Script to download RefSeq CDS and GFF files using NCBI datasets.

This script downloads genome data for any family from RefSeq and extracts CDS and GFF files.
It focuses on chromosome-level assemblies for better quality data.
"""

import os
import sys
import subprocess
import zipfile
import shutil
import argparse
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to NCBI datasets tool
DATASETS_TOOL = "/home5/ibirchl/Bioinformatics_tools/datasets"

class RefSeqDataDownloader:
    def __init__(self, output_dir="refseq_data", datasets_tool=DATASETS_TOOL):
        self.output_dir = Path(output_dir)
        self.datasets_tool = datasets_tool
        self.cds_dir = self.output_dir / "cds_files"
        self.gff_dir = self.output_dir / "gff_files"
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.cds_dir.mkdir(exist_ok=True)
        self.gff_dir.mkdir(exist_ok=True)
    
    def check_datasets_tool(self):
        """Check if the datasets tool is available and working."""
        try:
            result = subprocess.run([self.datasets_tool, "--version"], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"NCBI datasets tool version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Error accessing datasets tool: {e}")
            return False
    
    def get_available_species(self, family):
        """Get list of available species for a family from RefSeq with chromosome-level assemblies."""
        logger.info(f"Searching for available {family} species with chromosome-level assemblies...")
        
        try:
            # Search for the family with chromosome-level assemblies
            cmd = [
                self.datasets_tool, "download", "genome", "taxon", family,
                "--include", "cds,gff3",
                "--assembly-level", "chromosome",
                "--preview"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the JSON output to get record count
            if "record_count" in result.stdout:
                data = json.loads(result.stdout)
                record_count = data.get("record_count", 0)
                logger.info(f"Found {record_count} {family} genomes with chromosome-level assemblies and CDS/GFF annotations")
                
                if record_count > 0:
                    return [family]
                else:
                    logger.warning(f"No {family} genomes with chromosome-level assemblies found")
                    return []
            else:
                logger.warning(f"No {family} genomes with chromosome-level assemblies found")
                return []
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error searching for {family} species: {e}")
            return []
    
    def download_genome_data(self, family, include_cds=True, include_gff=True):
        """Download genome data for a specific family with chromosome-level assemblies."""
        logger.info(f"Downloading genome data for {family} (chromosome-level assemblies only)...")
        
        # Build the include parameter
        include_files = []
        if include_cds:
            include_files.append("cds")
        if include_gff:
            include_files.append("gff3")
        
        if not include_files:
            include_files = ["cds", "gff3"]  # Default to both
        
        include_param = ",".join(include_files)
        
        # Create a unique filename for this download
        filename = f"refseq_{family}_chromosome_data.zip"
        
        try:
            cmd = [
                self.datasets_tool, "download", "genome", "taxon", family,
                "--include", include_param,
                "--assembly-level", "chromosome",
                "--filename", filename
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Download completed for {family}")
            
            return filename
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading data for {family}: {e}")
            logger.error(f"stderr: {e.stderr}")
            return None
    
    def extract_and_organize_files(self, zip_filename, family):
        """Extract CDS and GFF files from the downloaded zip and organize them."""
        logger.info(f"Extracting and organizing files from {zip_filename}...")
        
        if not os.path.exists(zip_filename):
            logger.error(f"Zip file {zip_filename} not found")
            return False
        
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(f"temp_{family}")
            
            # Find and move CDS and GFF files
            temp_dir = Path(f"temp_{family}")
            
            # Look for CDS files (RefSeq format)
            cds_files = list(temp_dir.rglob("cds_from_genomic.fna"))
            for cds_file in cds_files:
                species_name = cds_file.parent.name
                new_name = f"{species_name}_{family}.fna"
                shutil.move(str(cds_file), str(self.cds_dir / new_name))
                logger.info(f"Moved CDS file: {new_name}")
            
            # Look for GFF files (RefSeq format)
            gff_files = list(temp_dir.rglob("*.gff"))
            for gff_file in gff_files:
                species_name = gff_file.parent.name
                new_name = f"{species_name}_{family}.gff"
                shutil.move(str(gff_file), str(self.gff_dir / new_name))
                logger.info(f"Moved GFF file: {new_name}")
            
            # Check if we found any files
            total_files = len(cds_files) + len(gff_files)
            if total_files == 0:
                logger.warning(f"No CDS or GFF files found for {family}. This may indicate:")
                logger.warning("  - The genome assemblies don't have gene annotations")
                logger.warning("  - Annotations are in a different format")
                logger.warning("  - Only raw genome sequences are available")
                
                # List what files are actually available
                all_files = list(temp_dir.rglob("*"))
                logger.info(f"Available files in {family} dataset:")
                for file_path in all_files:
                    if file_path.is_file():
                        logger.info(f"  - {file_path.relative_to(temp_dir)}")
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            # Remove the zip file
            os.remove(zip_filename)
            
            return total_files > 0
            
        except Exception as e:
            logger.error(f"Error extracting files: {e}")
            return False
    
    def download_family_data(self, family, include_cds=True, include_gff=True):
        """Download data for a specific family with chromosome-level assemblies."""
        available_species = self.get_available_species(family)
        
        if not available_species:
            logger.error(f"No {family} species with chromosome-level assemblies found")
            return False
        
        logger.info(f"Found {len(available_species)} {family} taxa with chromosome-level assemblies")
        
        success_count = 0
        for taxon in available_species:
            logger.info(f"Processing {taxon}...")
            
            # Download the data
            zip_filename = self.download_genome_data(taxon, include_cds, include_gff)
            
            if zip_filename:
                # Extract and organize the files
                if self.extract_and_organize_files(zip_filename, taxon):
                    success_count += 1
                    logger.info(f"Successfully processed {taxon}")
                else:
                    logger.error(f"Failed to extract files for {taxon}")
            else:
                logger.error(f"Failed to download data for {taxon}")
        
        logger.info(f"Successfully processed {success_count}/{len(available_species)} taxa")
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="Download RefSeq CDS and GFF files for any family using NCBI datasets")
    parser.add_argument("--family", required=True,
                       help="Family name to download (e.g., gobiidae, apogonidae, salmonidae)")
    parser.add_argument("--output-dir", default="refseq_data", 
                       help="Output directory for downloaded files (default: refseq_data)")
    parser.add_argument("--no-cds", action="store_true", 
                       help="Skip downloading CDS files")
    parser.add_argument("--no-gff", action="store_true", 
                       help="Skip downloading GFF files")
    parser.add_argument("--datasets-tool", default=DATASETS_TOOL,
                       help=f"Path to NCBI datasets tool (default: {DATASETS_TOOL})")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = RefSeqDataDownloader(args.output_dir, args.datasets_tool)
    
    # Check if datasets tool is available
    if not downloader.check_datasets_tool():
        logger.error("NCBI datasets tool not available. Please check the path.")
        sys.exit(1)
    
    # Determine what to include
    include_cds = not args.no_cds
    include_gff = not args.no_gff
    
    if not include_cds and not include_gff:
        logger.error("At least one of CDS or GFF files must be downloaded")
        sys.exit(1)
    
    # Download data
    logger.info(f"Downloading data for family: {args.family}")
    success = downloader.download_family_data(args.family, include_cds, include_gff)
    
    if success:
        logger.info("Download process completed successfully!")
        logger.info(f"CDS files saved to: {downloader.cds_dir}")
        logger.info(f"GFF files saved to: {downloader.gff_dir}")
    else:
        logger.error("Download process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
