#!/usr/bin/env python

from __future__ import absolute_import, print_function, division
from fileParseError import FileParseError
from medication import Medication
from absl import app
from absl import flags
import re
import sys

# * abseil flags
FLAGS = flags.FLAGS

flags.DEFINE_string('input', None, 'Input file name.')
flags.DEFINE_string('output', "sys.stdout", 'Output file name. [sys.stdout]')

flags.register_validator('input',
                         lambda value: value.endswith('.csv'),
                         message='--input must be a csv file')
flags.mark_flag_as_required('input')

medlist_list = [
    'anticholinergics.medlist',
    'antihypertensives.medlist']

def loadMedicationFile(file):
    ''' 
    loads a .medlist file 
    tsv separated by CLASS  SUBCLASS    GENERIC
    '''
    return_list = []
    if not file.endswith('.medlist'):
        raise FileParseError('%s needs to be a .medlist file\n' % file)
    with open(file, 'r') as f:
        for line in f:
            # comment line, ignore
            if line.startswith('#'):
                continue
            l = [x.strip() for x in line.split('\t')]
            _class = l[0]
            _subclass = l[1]
            _generic = l[2]
            return_list.append(Medication(_class, _subclass, _generic))
    return return_list

def loadMedications(files):
    """Loads medlists in the files list
    
    Arguments:
        files {absolute file paths}
    
    Returns:
        string[] meds -- list of Medication class objects    
    """
    meds = []
    for medlist in files:
        temp_meds = loadMedicationFile(medlist)
        meds.extend(temp_meds)
    return meds

def quick_dictionary_update(dictionary, key, step):
    if key not in dictionary:
        dictionary[key] = 0
    dictionary[key] += step

def main(argv):
    # load medications
    medications = loadMedications(medlist_list)
    # load patients file   
    with open(FLAGS.input, 'r') as f:
        all_lines = f.readlines()
        header = all_lines[0] 
        patients = all_lines[1:]# remove header
    # patients header is: patient_id, systolic_blood_pressure, medication_list
    new_header = header.split()
    # add column for class, subclass, type
    classes = list(set([x._class() for x in medications]))
    subclasses = list(set([x._subclass() for x in medications]))
    generics = list(set([x._generic() for x in medications]))
    new_header.extend([re.sub(r'[-()]','',x.replace(' ','_')) for x in classes])
    new_header.extend([re.sub(r'[-()]','',x.replace(' ','_')) for x in subclasses])
    new_header.extend([re.sub(r'[-()]','',x.replace(' ','_')) for x in generics])
    # to_write: list of lines for new file
    to_write = [','.join(new_header)]
    # get meds from each patient
    for patient in patients:
        splitted = patient.split(',',2)
        patient_id = splitted[0]
        systolic_bp = splitted[1]
        patient_meds = splitted[2]
        patient_detected_meds = []
        for med in medications:
            # make re object
            re_med = r'(^|\W|\d)%s($|\W|\d)' % med._generic().lower()
            if bool(re.search(re_med, patient_meds.lower())):
                patient_detected_meds.append(med)
        # patient_list contains id, systolic bp, meds
        patient_list = map(lambda x: x.strip(), splitted)
        # now we need to go through the classes, subclasses, and each med and count how many occurences there are
        # classes
        patient_dictionary = {}
        for med in patient_detected_meds:
            # update class
            quick_dictionary_update(patient_dictionary, med._class(), 1)
            # update subclass
            quick_dictionary_update(patient_dictionary, med._subclass(), 1)
            # update generic
            quick_dictionary_update(patient_dictionary, med._generic(), 1)
        # format in the correct order 
        # add patient_list
        for c in classes:
            if c in patient_dictionary:
                patient_list.append(patient_dictionary[c])
            else:
                patient_list.append('0')
        for s in subclasses:
            if s in patient_dictionary:
                patient_list.append(patient_dictionary[s])
            else:
                patient_list.append('0')
        for g in generics:
            if g in patient_dictionary:
                patient_list.append(patient_dictionary[g])
            else:
                patient_list.append('0')
        patient_final_string = ','.join(map(str, patient_list))
        to_write.append(patient_final_string) 
    to_write = '\n'.join(to_write)

    if FLAGS.output == 'sys.stdout':
        sys.stdout.write(to_write)
    else:
        with open(FLAGS.output, 'w') as f:
            f.write(to_write)   

if __name__ == '__main__':
    app.run(main)