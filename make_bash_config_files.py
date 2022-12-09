import sys, glob, os, yaml
import numpy as np
import pandas as pd

def make_single_drug_bash_script(script_outFile, out_dir, yaml_prefix, num_config_files, drug, drug_abbr):
    '''
    Arguments:
    
        script_outFile: the .sh file to create (if one with the same name exists, it will be overwritten)
        out_dir: the output analysis directory. It is the same one listed within each config file
        yaml_prefix: the format for these .sh scripts is a prefix followed by a number. This should be either binary, atu, or mic to reflect the types of analyses
        num_config_files: the total number of config_files to write to this script
        drug: full drug name, i.e. Isoniazid
        drug_abbr: drug abbreviation, i.e. INH
    '''
    
    assert yaml_prefix in ["binary", "atu", "mic"]
    
    with open(script_outFile, "w+") as file:
        
        # write the drug name and abbreviation
        file.write(f'drug="{drug}"\n')
        file.write(f'drug_abbr="{drug_abbr}"\n\n')
        
        # write the config_file array
        file.write("# list of config files to use\n")
        file.write("config_array=(\n")
        
        for i in range(1, num_config_files+1):
            
            # if the number is less than 10, add a 0 in front of it to keep them in order
            if i < 10:
                num_str = f"0{i}"
            else:
                num_str = str(i)
        
            file.write(f" 'config_files/{yaml_prefix}_{num_str}.yaml'\n")
            
        file.write(")\n\n")
        
        # write scripts to run for each config file
        file.write('for i in ${!config_array[@]}; do\n')
        file.write('    python3 -u 01_make_model_inputs.py "${config_array[$i]}" "$drug" "$drug_abbr"\n')
        file.write('    python3 -u 02_regression_with_bootstrap.py "${config_array[$i]}" "$drug" "$drug_abbr"\n')
        file.write('    python3 -u 03_model_analysis.py "${config_array[$i]}" "$drug" "$drug_abbr"\n')
        file.write('done\n\n')
        
        # write the final script
        file.write(f'python3 -u 04_compute_univariate_stats.py "$drug" "{yaml_prefix.upper()}" "{out_dir}"')

drug_abbr_dict = {"Delamanid": "DLM",
            "Bedaquiline": "BDQ",
            "Clofazimine": "CFZ",
            "Ethionamide": "ETH",
            "Linezolid": "LZD",
            "Moxifloxacin": "MXF",
            "Capreomycin": "CAP",
            "Amikacin": "AMI",
            "Pyrazinamide": "PZA",
            "Kanamycin": "KAN",
            "Levofloxacin": "LEV",
            "Streptomycin": "STM",
            "Ethambutol": "EMB",
            "Isoniazid": "INH",
            "Rifampicin": "RIF"
            }


# example to make all 15 bash scripts with the ATU config files
out_dir = "/home/ec2-user/who-mutation-catalogue"

for drug in drug_abbr_dict.keys():
    make_single_drug_bash_script(f"bash_scripts/run_{drug_abbr_dict[drug]}.sh", out_dir, "binary", 16, drug, drug_abbr_dict[drug])


# make directory to store config files if it doesn't exist
if not os.path.isdir("config_files"):
    os.mkdir("config_files")

# order of parameters to be updated: pheno_category_lst, tiers_lst, unpooled, synonymous, amb_mode
all_combos = [[["WHO"], ["1"], False, False, "DROP"],
              [["WHO"], ["1"], True, False, "DROP"],
              [["WHO"], ["1"], False, True, "DROP"],
              [["WHO"], ["1", "2"], False, False, "DROP"],
              [["WHO"], ["1", "2"], True, False, "DROP"],
              [["WHO"], ["1", "2"], False, True, "DROP"],
              [["ALL"], ["1"], False, False, "DROP"],
              [["ALL"], ["1"], True, False, "DROP"],
              [["ALL"], ["1"], False, True, "DROP"],
              [["ALL"], ["1", "2"], False, False, "DROP"],
              [["ALL"], ["1", "2"], True, False, "DROP"],
              [["ALL"], ["1", "2"], False, True, "DROP"],
              [["WHO"], ["1"], False, False, "AF"],
              [["WHO"], ["1", "2"], False, False, "AF"],
              [["ALL"], ["1"], False, False, "AF"],
              [["ALL"], ["1", "2"], False, False, "AF"]
            ]

# example set of kwargs -- KEEP UPDATED!
kwargs = yaml.safe_load(open("config.yaml"))


# config files run from 1 - len(all_combos)
for i in list(range(1, len(all_combos)+1)):
        
    # if the number is less than 10, add a 0 in front of it to keep them in order
    if i < 10:
        num_str = f"0{i}"
    else:
        num_str = str(i)
    
    with open(f"config_files/binary_{num_str}.yaml", "w+") as file:
        
        # constant for all cases
        kwargs["binary"] = True
        kwargs["atu_analysis"] = False
        
        if "model_prefix" in kwargs.keys():
            del kwargs["model_prefix"]
        
        # update param combinations and write to the file
        param_dict = dict(zip(["pheno_category_lst", "tiers_lst", "unpooled", "synonymous", "amb_mode"], all_combos[i-1]))
        kwargs.update(param_dict)
        yaml.dump(kwargs, file, default_flow_style=False, sort_keys=False)