There is a file called renderPDF.py . 

This file picks up the file for processing in line #545 
(ts_string_Devanagari = Path("output_text/updated-final-Devanagari.json").read_text(encoding="utf-8"))

You can change this file name to say output_text/test-mycopy.json 

Now create a file called test-mycopy.json in the output_text directory 

A json file is defined thus ( https://www.w3schools.com/whatis/whatis_json.asp )

So for our case we have a json file with the following structure

There is a top-level key called "supersection" 

This in turn has multiple keys e.g.  "supersection_6", "supersection_7" and so on

This is an example of a minimum working copy. You can copy this as test-mycopy.json . 

If you notice there is a "supersection_title" and a "subsection_title" but there is no "section_title" which is why "॥ प्रथमः खण्डः ॥", etc defined as "section_title" is dropped 

```json
{
    "supersection": {
        "supersection_6": {
            "supersection_title": "व्रत पर्व",
            "sections": {
                "count": {
                    "prev_count": 0,
                    "current_count": 19,
                    "total_count": 19
                },
                "section_81": {
                    "subsections": {
                        "subsection_785": {
                            "corrected-mantra_sets": [
                                {
                                    "corrected-mantra": "हुवे वाचाम् (ति) । वाचं(क) वाचं(थ) हुवे(ट्य) वाक्(त) । श्रुणोतु श्रुणोतु(च) वा(ट)गुवाक्(त) ।",
                                    "corrected-swara": ""
                                },
                                {
                                    "corrected-mantra": "समेतु समै(च) तुवा (ट्य) गुवाक्(त) । रमतां(कि) रमतां(क्रि) रमा(ट्रूट) ता(ख)",
                                    "corrected-swara": ""
                                },
                                {
                                    "corrected-mantra": "औहोवा(श) । ईहा ईहा ईहा(ग) ॥ १ ॥",
                                    "corrected-swara": ""
                                },
                                {
                                    "corrected-mantra": "हूवाइ(च्यशच) वाचासू । वाचं(क) हूवाइ(च) । वाक्(त) श्रुणोतुवा(कफप्ल) ग्वाक्(त) ।",
                                    "corrected-swara": ""
                                },
                                {
                                    "corrected-mantra": "समेतु(च्यश) सामै(क) तु(फध्य) बा(त) ग्वाक् । रमतां(टि) रमतो(टि) रमत् औहोवा(शग) ।",
                                    "corrected-swara": ""
                                },
                                {
                                    "corrected-mantra": "मायि(त) मायि मायि(श) ॥ २ ॥",
                                    "corrected-swara": ""
                                }
                            ],
                            "header": {
                                "header": "वाचो व्रते द्वे ।"
                            },
                            "mantra_sets": []
                        }
                    }
                }
            }
        }
    }
}
```