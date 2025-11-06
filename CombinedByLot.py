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
pro_BothReports = jmp.run_jsl('''

Names Default To Here(1);

prowin_Both = New Window( 
    "Enter Project ID",
	<<Modal,
	<<Return Result,
	value = Text Edit Box( "",<<Set Width(400) ),
	H List Box(
		Button Box("OK"),
        Button Box("Cancel")
	    )
    );

If (prowin_Both["Button"] != 1,
    Show( "Run Cancelled" );
    project_Both = "Run Cancelled";
    );

If (prowin_Both["button"] == 1, 
	project_Both = prowin_Both["value"]);
 
for_export_BothReports = project_Both;
PythonConnection = Python Connect();
PythonConnection << Send(for_export_BothReports, Python Name("user_entered_project"));
''')

# Variable transformation from JMP to Python
defined_project = user_entered_project
if defined_project == "Run Cancelled": 
    raise ValueError("Run was cancelled by user.")
    SystemExit()
    
#Combine identifier with defined project
project_identifier = "PRO"
PROJECT_ID = project_identifier + defined_project  #hardcoded for now to demo

# --------------------

# Generate Report #1 - Product, Avg Result, and Parameter Report
report_avgValues = FullAnalyticalReport(
    report_type_id="ALB#RET42", # "View all Products with their Results and Parameters by lot"
    description= "Temporary JMP Report -Prod Results Param",
    project_id = PROJECT_ID,
    name = f"Temporary JMP report for project {PROJECT_ID} - Prod Res Prm",
    input_data = {
        "project": [PROJECT_ID]
    },
    reportV2=True,
)
# Create Dataframe to Store Albert Data - View All Products with results and Parameters
registered_report_avgValues = client.reports.create_report(report=report_avgValues)
full_report_avgValues = client.reports.get_full_report(report_id=registered_report_avgValues.id)
dataframe_avg = full_report_avgValues.get_raw_dataframe() 

# ---------------------------------------------------

#Generate All Raw Data Values Report
report_allResults = FullAnalyticalReport(
    report_type_id="ALB#RET32", # "All Result Data (Every Row)"
    description= "Temporary JMP Report -All Results",
    project_id = PROJECT_ID,
    name = f"Temporary JMP report for project {PROJECT_ID} - Prod Res Prm",
    input_data = {
        "project": [PROJECT_ID]
    },
    reportV2=True,
)
# Create Dataframe to Store Albert Report Data -- All Results Report
registered_report_allResults = client.reports.create_report(report=report_allResults)
full_report_allResults = client.reports.get_full_report(report_id=registered_report_allResults.id)
dataframe_allResults = full_report_allResults.get_raw_dataframe() 


# Delete both reports in Albert
client.reports.delete(id=registered_report_avgValues.id)
client.reports.delete(id=registered_report_allResults.id)

# ----------------------------------------------------------
## Create View all Products with Results and Parameters Dataframe manipulation for JMP
# Mix Albert and JMP together
df_avg = dataframe_avg

# create JMP DataTable from pandas DataFrame Avg Values
dt_avg_title = f"Albert Formula & Avg Data - {defined_project}"
dt_avg = jmp.DataTable(dt_avg_title, df_avg.shape[0])

# get the column names from the data frame
names = list(df_avg.columns)

# loop across the columns of the data frame
for j in range( df_avg.shape[1] ):

    # check if the column data type is string or numeric
	if is_string_dtype(df_avg[ names[j] ] ):
		dt_avg.new_column(names[j], jmp.DataType.Character )
	else:
		dt_avg.new_column(names[j], jmp.DataType.Character )
		
	# populate the JMP column with data
	dt_avg[j] = list(df_avg.iloc[:,j])

# ------------------------------------------------------------------------------
## Create All Results Dataframe manipulation for JMP
# Mix Albert and JMP together
df_all = dataframe_allResults

# create JMP DataTable from pandas DataFrame
dt_all_title = f"Albert Raw Result Data - {defined_project}"
dt_all = jmp.DataTable(dt_all_title, df_all.shape[0])

# get the column names from the data frame
names = list(df_all.columns)

# loop across the columns of the data frame
for j in range( df_all.shape[1] ):

    # check if the column data type is string or numeric
	if is_string_dtype(df_all[ names[j] ] ):
		dt_all.new_column(names[j], jmp.DataType.Character )
	else:
		dt_all.new_column(names[j], jmp.DataType.Character )
		
	# populate the JMP column with data
	dt_all[j] = list(df_all.iloc[:,j])
 
  ## Join 
join_script = f"""
Names Default To Here(1);
dtAll = Data Table("{dt_all_title}");
dtAvg = Data Table("{dt_avg_title}");

dtJoined = dtAvg << Join(
    With(dtAll),
	Select( :"Product / Formula ID"n ),
	Select( :"Product / Formula Name"n ),
	Select( :"Lot Number"n),
	Select( :Sheet Name, :Task Name, :Task ID ),
	SelectWith( :Created By, :Created At ),
	Select( :Type, :"Name (Inventory, Result, Parameter)"n, :Interval, :Value ),
	SelectWith( :Row, :Value ),
	By Matching Columns(
		:"Product / Formula ID"n = :"Product / Formula ID"n,
		:"Product / Formula Name"n = :"Product / Formula Name"n,
		:"Lot Number"n = :"Lot Number"n,
		:"Name (Inventory, Result, Parameter)"n = :"Result"n,
		:Task ID = :Task ID,
		:Interval = :Interval
		),
	Drop multiples( 0, 0 ),
	Include Nonmatches( 1, 1 ),
	Preserve main table order( 1 ),
);

//Name Joined Table: 
dtJoined << Set Name("Albert Combined Lot Data - {defined_project}");
dtJoined << Bring Window To Front;

//Rename Value Columns: 
Column ( dtJoined, "Value of Albert Formula & Avg Data - {defined_project}" ) << Set Name( "Average Value" );
Column ( dtJoined, "Value of Albert Raw Result Data - {defined_project}" ) << Set Name( "Raw Value" );

// Close the source tables quietly:
Close(dtAvg, NoSave);
Close(dtAll, NoSave);
"""
jmp.run_jsl(join_script)