import google.generativeai as genai



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