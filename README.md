The config file should look like below:
The following tree structure has to be followed for the script to read it
The primary column should be the column on which you are querying for:

For Example : If you want to get all the patients with a status of "Deceased" then PAT_ID would be the primary column. The primary column should be also present in all other dataclasses or select conditions as well

If "PRIMARY_COLUMN_Path" and "PRIMARY_COLUMN_Output" are provided,then an output file will be generating with all the unique values of the primary column which can be later used for comparison or for other calculations.

The "SELECT" parameter is a required parameter and can have multiple select queries which can be applied for each dataclass
The following parameters can be added to the select container:

1) Path:
	This is a required parameter which specifies the path/directory of the files on which the select query has to run
2)DataClass:
3)USECOLS:
	This is an optional parameter provided and can have the following values.
	If you need to select all the columns, then you can specify ["*"] as the value for USECOLS
	If you need to select only specific columns, then you can specify the column names as a list, for ex: ["A","B"]
	If not provided, then the output would have the primary column and the columns on which the select query has been applied
4)COLUMNS:
	The COLUMNS parameter is a required array of columns on which the select query has to be applied:
	It has a specific format which needs to be followed:
	COLUMNNAME:constraint:NOTNULL
	COLUMNNAME:value:['A',B]
	COLUMNNAME:startsWith:['A','B']

	OPERATOR:
		The OPERATOR paramter has to be specified if there are multiple columns contained in the COLUMNS Array
		The OPERATOR can be either '&' or '|' values.
	Output:
		The Output parameter is a required which will generate the output file for the specific select quiery in the specified filename



{
  "CUSTOMERS": {
    "AURORA": {
      "PRIMARY_COLUMN": "PAT_ID",  ====== Required ======
      "PRIMARY_COLUMN_Path": "Patient/", ====== Required, can leave empty if not needed ======
      "PRIMARY_COLUMN_Output": "OutputDir/output-aurora-primary-list.csv", ====== Required, can leave empty if not needed ======
      "SELECT": [
        {
          "Path": "CAssessment/", ====== Required ======
          "DataClass": "CancerAssessment",
          "USECOLS":["*"],
          "COLUMNS": [		====== Required ======
            "BODY_SITE_NAME:value:NOTNULL"
          ],
          "Output": "OutputDir/output-cancerassessment.csv" ==== Required ====

        },
        {
          "Path": "Diagnosis/",
          "DataClass": "Diagnosis",
          "COLUMNS": [
            "ICD9_CODE:range:[140-239.9]",
            "ICD10_CODE:startsWith:['C','D0','D1','D2','D3','D4']"
          ],
          "Output": "OutputDir/output-diagnosis.csv"

        }
      ],
      "OUTPUT": {
        "DIR": "OutputDir/",
        "filename": "output-summary.csv"
      }
    }
  }
}
