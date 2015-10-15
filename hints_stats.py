import pandas as pd
import datetime
import paramiko
import sys

IP = "webwork.cse.ucsd.edu"
USERNAME = "werner"
ssh_private_key='/home/woerns/.ssh/id_rsa'

def get_table():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP, username=USERNAME, key_filename=ssh_private_key)
    
    command = """mysql -u readonly -preadonly webwork -e 'select * from 		CSE103_Fall2015_assigned_hint;'
    """

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    #print ssh_stderr.read()
    data = ssh_stdout.readlines()
    ssh.close()
    
    header = data[0].strip().split('\t')
    table = []
    for line in data[1:]:
        line = line.strip()
        entries = line.split('\t')
        table.append(entries)  

    df = pd.DataFrame(table,columns=header)

    df['id'] = df['id'].apply(int)
    df['problem_id'] = df['problem_id'].apply(int)
    df['hint_id'] = df['hint_id'].apply(int)
    df['assigned'] = df['assigned'].apply(int)
    
    return df

def generate_hint_stats(set_id):
    df = get_table()
    dfSet = df.ix[df['set_id']==set_id]
    dfSet = dfSet.groupby(['problem_id','pg_id','hint_html'])

    HintStatistics = {}
    
    for name,group in dfSet:
        problem_id,pg_id,hint_html = name
        key = (problem_id,pg_id,hint_html)
        if not key in HintStatistics.keys():
            HintStatistics[key]={'could_sent':0, 'sent':0}
        HintStatistics[key]['could_sent'] = len(group['assigned'])
        HintStatistics[key]['sent'] = sum(group['assigned'])

    print 'Hint statistics for %s at time=%s'%(set_id,str(datetime.datetime.now()))
    print 'problem\tpart\t\thint\t\t\tcould_sent\tsent\tsent[%]'
    for key in HintStatistics.keys():
        row = HintStatistics[key]
	HINT_LEN = 20
	hint = key[2][:HINT_LEN-4]+"..."
	diff = HINT_LEN-len(hint)
	if diff>0:
	    hint = hint + diff*" "    # make hints to same length for display
        print "%2d\t%s\t%s\t%d\t\t%d\t%3.2f"%(key[0],key[1],hint,row['could_sent'],row['sent'],\
                                                row['sent']*100.0/row['could_sent'])

if __name__=='__main__':

    try:
        if len(sys.argv)==2: 
	    set_id = sys.argv[1].capitalize()
	    generate_hint_stats(set_id)
	else:
	    print "Requires assignment number as input (e.g. week3)"   
    except:
	    print "Requires assignment number as input (e.g. week3)"   
