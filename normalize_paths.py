#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
One-time migration script to normalize all paths in the database
Run this script once to fix any existing paths with mixed separators
"""

import os
import sys
from PfModel import gDatabase, PfAnalysis

def normalize_analysis_paths():
    """Normalize result_directory paths in all analyses"""

    print("Normalizing paths in PhyloForester database...")
    print(f"Database: {gDatabase.database}")
    print("-" * 60)

    try:
        # Connect to database
        gDatabase.connect(reuse_if_open=True)

        # Get all analyses
        analyses = PfAnalysis.select()
        total_count = analyses.count()
        updated_count = 0

        print(f"Found {total_count} analyses to check")
        print()

        for analysis in analyses:
            if analysis.result_directory:
                original = analysis.result_directory
                normalized = os.path.normpath(original)

                # Only update if path changed
                if original != normalized:
                    print(f"Updating analysis ID {analysis.id}:")
                    print(f"  Before: {original}")
                    print(f"  After:  {normalized}")

                    analysis.result_directory = normalized
                    analysis.save()
                    updated_count += 1
                    print()

        print("-" * 60)
        print(f"Migration complete!")
        print(f"  Total analyses: {total_count}")
        print(f"  Updated: {updated_count}")
        print(f"  Unchanged: {total_count - updated_count}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if not gDatabase.is_closed():
            gDatabase.close()

    return 0

if __name__ == "__main__":
    sys.exit(normalize_analysis_paths())
