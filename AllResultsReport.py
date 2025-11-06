import jmp
import jmputils
jmputils.jpip('install', 'truststore')
jmputils.jpip('install --upgrade', 'pip setuptools certifi')
jmputils.jpip('install', 'certifi')
jmputils.jpip('install', 'albert') 
jmputils.jpip('install', 'numpy')
jmputils.jpip('install', 'pandas')

import truststore
import numpy as np
import pandas as pd

from pandas.api.types import is_numeric_dtype, is_string_dtype
from albert.resources import reports
from albert.resources.reports import FullAnalyticalReport
from albert import Albert

#Setup SSL Verification - Active directory 
truststore.inject_into_ssl()

#Pull Email Auth
USER_EMAIL = user_submitted_email

#SSO Validation
client = Albert.from_sso(
    base_url= "https://app.albertinvent.com",
    email= USER_EMAIL,
    port=5000,  # 5000 is default; change as needed
)
#JMP Script - Pop-up for entering Project ID
pro_AllResults = jmp.run_jsl('''

Names Default To Here(1);
                            
prowin_All = New Window( 
    "Enter Project ID",
	<<Modal,
	<<Return Result,
	value = Text Edit Box( "",<<Set Width(400) ),
	H List Box(
		Button Box("OK"),
        Button Box("Cancel")
	    )
    );

If (prowin_All["Button"] != 1,
    Show( "Run Cancelled" );
    project_all = "Run Cancelled";
    );

If (prowin_All["Button"] == 1, 
	project_all = prowin_All["value"];
    );

for_export_allResults = project_all;
PythonConnection = Python Connect();
PythonConnection << Send(for_export_allResults, Python Name("user_entered_project"));
''')

# Variable transformation from JMP to Python
defined_project = user_entered_project
if defined_project == "Run Cancelled": 
    raise ValueError("Run was cancelled by user.")
    SystemExit()
    
#Combine identifier with defined project
project_identifier = "PRO"
PROJECT_ID = project_identifier + defined_project  
# Report Structure
report = FullAnalyticalReport(
    report_type_id="ALB#RET32", # "All Result Data (Every Row)"
    description= "Temporary JMP Report - All Results",
    project_id = PROJECT_ID,
    name = f"Temporary JMP report for project {PROJECT_ID} - All Results",
    input_data = {
        "project": [PROJECT_ID]
    },
    reportV2=True,
)

registered_report = client.reports.create_report(report=report)
full_report_allresults = client.reports.get_full_report(report_id=registered_report.id)
dataframe = full_report_allresults.get_raw_dataframe() # Here is the Dataframe you need!
print(dataframe.head()) #Confirmation testing only

# Delete report in Albert
client.reports.delete(id=registered_report.id)

# Mix Albert and JMP together
df = dataframe

# create JMP DataTable from pandas DataFrame
dt_title = f'Albert Raw Result Data - {defined_project}'
dt = jmp.DataTable(dt_title, df.shape[0])

# get the column names from the data frame
names = list(df.columns)

# loop across the columns of the data frame
for j in range( df.shape[1] ):

    # check if the column data type is string or numeric
	if is_string_dtype(df[ names[j] ] ):
		dt.new_column(names[j], jmp.DataType.Character )
	else:
		dt.new_column(names[j], jmp.DataType.Character )
		
	# populate the JMP column with data
	dt[j] = list(df.iloc[:,j])
