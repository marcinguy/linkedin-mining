import csv
import mysql.connector
import argparse
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')


if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='sql import')
        parser.add_argument('-i','--input', help='input file', required=True)
        args = parser.parse_args()
        inputf = args.input

mydb = mysql.connector.connect(user='root', password='root',
                                     host='localhost',
                                     database='linkedin_miner')


cursor = mydb.cursor()

csv_data = csv.reader(file(inputf))
for row in csv_data:
    print row


    cursor.execute("INSERT INTO samplesheet(Person,Website,Official_Title,Location,Time_Entered,User_Entered,Company,Position,Department,Assistant,Reports_To,Start,Duration,Previous_Company,Previous_Print_Name,Previous_Official_Title,Prior_Companies,Time_Updated,User_Updated,Update_History,Preferred_Email,Resume_File,Last_Name,First_Name,Home_Phone,Work_Phone,Other_Phone_1,Other_Phone_Description_1,Other_Phone_2,Other_Phone_Description_2,Other_Phone_3,Other_Phone_Description_3,Personal_Email_1,Personal_Email_2,Work_Email,Home_Address_1,Home_Address_2,Home_City,Home_Region,Home_Postal_Code,Home_Country,Resume_Text,Attributes,p_id,status,Resume_Text_Html) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,'pending',NULL)",row)




#close the connection to the database.
mydb.commit()
cursor.close()
print "Done"
