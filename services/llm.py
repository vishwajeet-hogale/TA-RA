import google.generativeai as genai
import time 


genai.configure(api_key="AIzaSyC5p0A8JzIsVleLBLPxHSxo1ae_ByGS3ho")
def get_all_info_prof_page(text):
    
    
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(f"""{text}\n\n\n\n\n\n\n 
                                      Extract all the information from the text in the following way : 
                                      Research Interests 
                                      - interest 1
                                      - interest 2 

                                      Biography
                                      - ... 

                                      Recent Publications 
                                      - publication 1 
                                      - publication 2

                                      Qualifications :
                                      - ...

                                                    """)
    return response.text


def generate_mail(df,resume):
    ta, ra = [],[]
    model = genai.GenerativeModel('gemini-1.0-pro-latest')

    for val,row in df.iterrows():
        prof_name = row["Name"]
        bio = row["Biography"]
        ongoing_research_abstract = row["Abstract"]
        try : 
            response_ta = model.generate_content(f"""\n\n
                                                Professor name : {prof_name}\n
                                                Biography : {bio}\n
                                                On going research abstract : {ongoing_research_abstract}\n
                                                My resume : {resume} 

                                                Use the above information and craft a good mail to the professor asking him for TA roles. Use my resume and all his info as reference. 

                                                        """)
            time.sleep(1)
            response_ra = model.generate_content(f"""\n\n
                                                Professor name : {prof_name}\n
                                                Biography : {bio}\n
                                                On going research abstract : {ongoing_research_abstract}\n
                                                My resume : {resume} 

                                                Use the above information and craft a good mail to the professor asking him for RA roles. Use my resume and all his info as reference. 

                                                        """)
            time.sleep(1)
            print(response_ta.candidates[0].content.parts[0].text)
            ta.append(response_ta.candidates[0].content.parts[0].text)
            ra.append(response_ra.candidates[0].content.parts[0].text)
        except:
            ta.append("")
            ra.append("")
    df["TA_mail"] = ta 
    df["RA_mail"] = ra
    return df
