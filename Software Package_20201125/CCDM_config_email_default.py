#CCDM Default email config file
#To create a custom file  and make use of CCDM email logs, perfrom the following:
#1 - save this file with the "_default" portion removed from the name
#2 - fill in the required information below and save
#3 - Ensure ENABLE_DAILY_EMAILS variable in CCDM_config.py file is set to True


EMAIL_config = {
                "from": "someone@somedomain.ca",
                "to": "someoneelse@someotherdonain.ca",
                "subject": "CCDM - Daily solar log",
                "smtp_host": "add smtp host here",
                "smtp_port": "add smtp port here",
                "username": "add user name for the sending email account",
                "password": "add password for the sending email account"
                }    
