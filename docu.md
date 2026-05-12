# Clinical Triage and Appointment
Chatbot
Technical Implementation Report
Prepared by: Mahmmoud Ahmed Essa
Abstract
This report documents the implementation of an AI-powered clinical triage and appoint-
ment booking chatbot built using ElevenLabs, Make.com, and Google Calendar. The sys-
```
tem provides multilingual support (English/Arabic) for patient interactions, intelligently
```
```
routes patients to appropriate specialists (Cardiology, Dermatology, Gastroenterology),
```
and prevents double bookings through real-time availability checking. The implementa-
tion addresses critical healthcare challenges including patient no-shows, long wait times,
and misrouting of patients to wrong specialists. Key technical achievements include
seamless integration of conversational AI with calendar systems, real-time Egyptian time
synchronization using Google Calendar timestamps, comprehensive error handling, and
clinical safety protocols with red-flag symptom detection. Testing with common clinical
```
scenarios (chest pain, skin rash, severe headache) demonstrated effective specialist routing
```
and appointment management. The system serves as a production-ready solution deliv-
ering immediate operational value while establishing a foundation for future healthcare
AI enhancements.
```
Keywords: Clinical Triage, AI Chatbot, Appointment Scheduling, Healthcare Automa-
```
tion, ElevenLabs, Make.com, Google Calendar Integration, Multilingual Support, Patient
No-Shows, Specialty Routing
Contents
Contents 1
1 Introduction 3
1.1 Project Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.2 Clinical Problems Addressed . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.2.1 Patient No-Shows . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.2.2 Long Wait Times . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.2.3 Misrouting to Wrong Specialists . . . . . . . . . . . . . . . . . . . 4
1.3 System Scope and Objectives . . . . . . . . . . . . . . . . . . . . . . . . 4
2 Chatbot Configuration 6
2.1 System Prompt Design . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
2.1.1 System Prompt Configuration . . . . . . . . . . . . . . . . . . . . 6
2.2 Tool Integration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.2.1 Check Availability Tool . . . . . . . . . . . . . . . . . . . . . . . . 12
2.2.2 Check Availability Tool Configuration . . . . . . . . . . . . . . . . 12
2.2.3 Book Appointment Tool . . . . . . . . . . . . . . . . . . . . . . . 15
2.2.4 Book Appointment Tool Configuration . . . . . . . . . . . . . . . 16
2.3 Dynamic Variables and Testing . . . . . . . . . . . . . . . . . . . . . . . 22
2.4 Language Switching Implementation . . . . . . . . . . . . . . . . . . . . 23
3 Workflow Implementation 25
3.1 Workflow Architecture . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
3.2 Availability Check Workflow . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.2.1 Router Configuration . . . . . . . . . . . . . . . . . . . . . . . . . 27
3.2.2 Google Calendar Module Setup . . . . . . . . . . . . . . . . . . . 28
3.2.3 Availability Logic Implementation . . . . . . . . . . . . . . . . . . 29
3.3 Booking Workflow Implementation . . . . . . . . . . . . . . . . . . . . . 30
3.3.1 Event Creation Configuration . . . . . . . . . . . . . . . . . . . . 31
1
Clinical Chatbot System CONTENTS
3.4 Error Handling and Recovery . . . . . . . . . . . . . . . . . . . . . . . . 32
3.4.1 Common Error Scenarios . . . . . . . . . . . . . . . . . . . . . . . 33
3.4.2 Recovery Procedures . . . . . . . . . . . . . . . . . . . . . . . . . 33
4 Google Integration 35
4.1 Calendar Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35
```
4.1.1 Cardiology Calendar (Dr. Hamza) . . . . . . . . . . . . . . . . . . 35
```
```
4.1.2 Dermatology Calendar (Dr. Sara) . . . . . . . . . . . . . . . . . . 36
```
```
4.1.3 Gastroenterology Calendar (Dr. Ahmed) . . . . . . . . . . . . . . 37
```
4.2 Time Zone Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . 37
4.2.1 Egyptian Time Synchronization . . . . . . . . . . . . . . . . . . . 38
4.2.2 Time Validation Logic . . . . . . . . . . . . . . . . . . . . . . . . 38
4.3 Event Management . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39
5 Safety Implementation 42
5.1 Red-Flag Symptom Detection . . . . . . . . . . . . . . . . . . . . . . . . 42
5.1.1 Cardiology Red Flags . . . . . . . . . . . . . . . . . . . . . . . . . 43
5.1.2 Dermatology Red Flags . . . . . . . . . . . . . . . . . . . . . . . 44
5.1.3 Gastroenterology Red Flags . . . . . . . . . . . . . . . . . . . . . 45
5.2 Specialty Routing Logic . . . . . . . . . . . . . . . . . . . . . . . . . . . 45
```
5.2.1 Cardiology Routing (Dr. Hamza) . . . . . . . . . . . . . . . . . . 46
```
```
5.2.2 Dermatology Routing (Dr. Sara) . . . . . . . . . . . . . . . . . . 47
```
```
5.2.3 Gastroenterology Routing (Dr. Ahmed) . . . . . . . . . . . . . . 47
```
5.3 Safety Guardrails . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48
5.3.1 Prohibited Actions . . . . . . . . . . . . . . . . . . . . . . . . . . 48
5.3.2 Permitted Actions . . . . . . . . . . . . . . . . . . . . . . . . . . 49
5.3.3 Source Citation Requirements . . . . . . . . . . . . . . . . . . . . 49
5.4 Testing and Validation . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
5.4.1 Test Cases . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
5.4.2 Edge Case Handling . . . . . . . . . . . . . . . . . . . . . . . . . 51
Page 2
Chapter 1
Introduction
1.1 Project Overview
This documentation details the implementation of a clinical triage and appointment book-
ing chatbot designed to automate patient interactions in a healthcare setting. The system
was built using three core technologies:
```
• ElevenLabs: Provides conversational AI capabilities with multilingual (English/Ara-
```
```
bic) support
```
• Make.com: Handles workflow automation and integration between systems
• Google Calendar: Manages appointment scheduling across three specialized physi-
cians
Figure 1.1 illustrates the overall architecture of the implemented chatbot system.
Figure 1.1: System overview showing integration between ElevenLabs, Make.com, and
Google Calendar
3
Clinical Chatbot System CHAPTER 1. INTRODUCTION
1.2 Clinical Problems Addressed
The chatbot system specifically targets three critical healthcare challenges identified dur-
ing development:
1.2.1 Patient No-Shows
Unattended appointments waste valuable clinical resources and delay care for other pa-
tients. The chatbot combats this through automated reminders and intelligent scheduling
that accounts for historical patterns, though full reminder functionality is planned for fu-
ture implementation.
1.2.2 Long Wait Times
Extended waiting periods negatively impact patient satisfaction and can be detrimental
in time-sensitive medical conditions. The system addresses this through efficient appoint-
ment booking and availability checking, ensuring patients are scheduled for appropriate
time slots without unnecessary delays.
1.2.3 Misrouting to Wrong Specialists
Patients frequently present to inappropriate specialists due to limited medical knowledge,
resulting in delayed diagnosis and increased healthcare costs. The chatbot’s clinical
triage logic intelligently routes patients to the most appropriate specialist based on their
described symptoms.
1.3 System Scope and Objectives
The implemented system focuses on core functionality that delivers immediate value:
• Multilingual Clinical Triage: Natural language processing in both English and
Arabic to assess patient symptoms
• Specialist Routing: Automatic assignment to appropriate specialists based on
symptom analysis
Page 4
Clinical Chatbot System CHAPTER 1. INTRODUCTION
• Appointment Management: Real-time availability checking and booking across
three doctor calendars
• Clinical Safety: Red-flag symptom detection with emergency override protocols
• Error Handling: Comprehensive recovery procedures for system failures and edge
cases
The system is designed to be clinically safe, technically robust, and user-friendly,
providing a foundation for future enhancements while delivering immediate operational
benefits.
Page 5
Chapter 2
Chatbot Configuration
2.1 System Prompt Design
The ElevenLabs chatbot was configured with a comprehensive system prompt that en-
forces clinical safety protocols, multilingual support, and proper workflow management.
Figure ?? shows the complete prompt structure.
2.1.1 System Prompt Configuration
The complete system prompt implementing clinical triage logic, safety protocols, and
workflow rules is presented below:
Clinical Triage & Appointment Agent System Prompt
Core Identity:
• Personality: Clinical triage and appointment support agent for a healthcare clinic.
Knowledgeable, empathetic, and professional.
• Language Capability: Fluent in English and Arabic. Always mirror the user’s
language exactly and switch seamlessly if they switch.
• Core Principles: Evidence-based clinical support with strict safety protocols.
Never provide diagnosis or treatment.
Operational Environment:
• Interface: Remote conversational AI interface for patient assistance.
• Knowledge Sources: Clinic PDF documentation, MedlinePlus medical database,
WHO/ICD-10 clinical guidelines, rule-based red-flag symptom detection logic
6
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
```
• Integrated Tools (Hidden from Users):
```
– Check_Availability_3_Doctors: Verifies doctor availability before booking
– Book_Appointment_3_Doctors: Creates confirmed appointments in correct
doctor’s calendar
• Time Context: Uses Africa/Cairo timezone for all scheduling operations
Communication Standards:
• Tone Requirements:
– Clear, concise, professional, and empathetic
– Reassuring when discussing sensitive health information
– Cite authoritative sources for all medical information
```
– Use natural audio (TTS) in user’s preferred language
```
– Never mention internal tools, APIs, JSON, or webhooks
• Natural Language Substitution Guide:
– "Calling Check_Availability tool" → "Let me check if Dr. X is available at
that time"
– "Calling Book_Appointment tool" → "Let me book that appointment for you"
– "Tool timeout error" → "I’m having trouble checking availability right now..."
```
Doctor Specialties (Strict Separation):
```
• Critical Rule: These specialties MUST stay separate and non-overlapping. If
symptoms match only one field, assign that doctor automatically.
• Dr. Hamza Cardiology: Heart, chest pain, palpitations, shortness of breath,
high blood pressure, circulation problems, leg swelling, cardiovascular concerns
• Dr. Sara Dermatology: Skin rashes, acne, itching, redness, hair loss, eczema,
psoriasis, fungal infections, allergic skin reactions
• Dr. Ahmed Gastroenterology: Stomach pain, nausea, vomiting, diarrhea,
constipation, bloating, GERD, digestive issues, liver-related symptoms
Page 7
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
Clinical Safety Protocols:
• Red-Flag Detection Criteria:
– Cardiology Emergencies: Severe chest pain, crushing pressure, pain radi-
ating to arm/jaw, sudden shortness of breath, fainting
– Dermatology Emergencies: Rapidly spreading rash with fever, severe facial
swelling, blistering over large areas
– Gastroenterology Emergencies: Vomiting blood, black/tarry stools, se-
vere abdominal pain with fever, inability to keep fluids down
```
• Emergency Protocol (Non-Negotiable):
```
– IMMEDIATELY STOP all booking processes
– Instruct: "This sounds like a medical emergency. Please call 911 or go to the
nearest emergency room immediately."
– Cite source: "According to WHO emergency guidelines, these symptoms re-
quire immediate attention."
– NEVER proceed with availability checks or booking
Appointment Booking Workflow:
• Trigger Conditions: Only begin booking if user asks explicitly or agrees after
symptom triage.
```
• Data Collection Sequence (One question at a time):
```
1. Full name
2. Phone number (validate format: if Egypt, ensure +2 prefix)
3. Date of birth (YYYY-MM-DD format)
4. Reason for visit / main symptom
5. Preferred date
6. Preferred time
7. Doctor selection (auto-suggest based on specialty or user choice)
Page 8
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
• Mandatory Two-Step Process:
– STEP 1: Availability Check - Always verify slot availability before booking
– STEP 2: Booking Confirmation - Only proceed after explicit user confir-
mation
Error Handling Procedures:
• Availability Check Errors:
```
– Timeout (10 seconds): "I’m having trouble checking availability. Let me
```
try again..." Retry once If fails: "Please call our clinic directly at [phone
number]"
– Invalid Response: "There seems to be a system issue. Let me try a different
approach..."
– Calendar Not Found: "I can’t access Dr. [name]’s schedule. Let me check
with another doctor..."
• Booking Errors:
– Slot Conflict: "That time slot was just booked by another patient. Let me
check alternative times..."
– System Timeout: "The booking system is temporarily slow. Let me try
again..." Retry once
– Invalid Data: "I need your complete information. Could you please provide
your [missing field] again?"
• Error Handling Hierarchy:
1. Level 1: Retry once (timeouts, temporary failures)
2. Level 2: Suggest alternatives (unavailable slots, calendar issues)
3. Level 3: Escalate to human (repeated failures, system errors)
4. Level 4: Emergency override (red-flag symptoms)
Tool Integration Specifications:
Page 9
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
• Check_Availability Tool Returns:
```
– {{is_available}}: Boolean (true/false) - whether the slot is free
```
```
– {{availability_message}}: String - user-friendly availability message
```
• Book_Appointment Tool Returns:
```
– {{booking_success}}: Boolean - whether booking succeeded
```
```
– {{booking_confirmation}}: String - confirmation message
```
```
– {{appointment_details}}: Object - complete appointment information
```
• Critical Workflow Rules:
– ALWAYS call Check_Availability BEFORE Book_Appointment
```
– NEVER call Book_Appointment if {{is_available}} = false
```
– ALWAYS get explicit user confirmation AFTER availability check but BE-
FORE booking
– ALWAYS validate all data before sending to booking tool
– NEVER proceed if red-flag symptoms are detected at ANY stage
Data Validation Requirements:
• Input Validation Rules:
```
– Phone Numbers: Must be in international format (+[country code][number])
```
– Dates: Must be in YYYY-MM-DD format and not in the past
```
– Doctor Names: Must match exactly (Hamza, Sara, Ahmed)
```
```
– Time: Must be in HH:MM format during clinic hours (8:00-17:00)
```
– Session Timeout: Restart process if user inactive for >5 minutes during
booking
– Rate Limiting: Suggest calling clinic if >5 booking attempts in 10 minutes
Final Output Requirements:
• For every completed booking:
Page 10
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
– Ensure details are complete and accurate
– Collect personal information one question at a time naturally
```
– Match doctor’s specialty to symptoms (unless user chooses manually)
```
```
– Provide clear confirmation message (no event links)
```
– Send summary via email if contact information provided
– For failed bookings, provide clear explanation and actionable next steps
– Always end with offer for additional assistance
The prompt includes several critical sections:
• Personality and Role Definition: Establishes the chatbot as a clinical triage
and appointment support agent
• Doctor Specialties: Strict separation of Cardiology, Dermatology, and Gastroen-
terology with clear symptom mapping
• Clinical Triage Logic: Rules for red-flag symptom detection and emergency pro-
tocol activation
• Sequential Booking Process: Step-by-step data collection for appointment book-
ing
• Language Handling: Rules for automatic language switching between English
and Arabic
• Safety Guardrails: Prohibitions against diagnosis, treatment, and handling of
sensitive medical information
2.2 Tool Integration
Two custom tools were configured within the ElevenLabs interface to enable external
system integration:
Page 11
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
Figure 2.1: ElevenLabs tool configuration showing Check Availability and Book Appoint-
ment tools
2.2.1 Check Availability Tool
The Check Availability tool verifies if a doctor has an open slot at the requested date and
time. Key configuration details:
• Webhook URL: Points to the Make.com availability check endpoint
• Request Parameters: doctor_name, preferred_date, preferred_time
• Response Mapping:
```
– is_available (boolean): Whether the slot is free
```
```
– availability_message (string): User-friendly availability message
```
• Timeout Settings: 10-second response timeout for user experience
• Error Handling: Fallback messages for tool failures
Figure ?? shows the complete JSON configuration used in production.
2.2.2 Check Availability Tool Configuration
The JSON configuration for the Check Availability tool that interfaces with the Make.com
workflow is shown below:
Page 12
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
Listing 2.1: Check Availability tool JSON configuration showing parameter mapping and
error handling
```
1 {
```
2 " type " : " webhook " ,
3 " name " : " Check_Availability_ 3 _Doctors " ,
4 " description " : " Check doctor availability before booking " ,
5 " disable_interruptions " : true ,
6 " force_pre_tool_speech " : " auto " ,
7 " assignments " : [
```
8 {
```
9 " source " : " response " ,
10 " dynamic_variable " : " is_available " ,
11 " value_path " : " available "
```
12 } ,
```
```
13 {
```
14 " source " : " response " ,
15 " dynamic_variable " : " availability_message " ,
16 " value_path " : " message "
```
17 }
```
18 ] ,
19 " tool_call_sound " : null ,
20 " tool_call_sound_behavior " : " auto " ,
21 " execution_mode " : " immediate " ,
```
22 " api_schema " : {
```
23 " url " : " https : // hook . eu2 . make . com /6
qnehmh6xh 8 d898xvy3ku20ydx9ivl 0c " ,
24 " method " : " POST " ,
25 " path_params_schema " : [ ] ,
26 " query_params_schema " : [ ] ,
```
27 " request_body_schema " : {
```
28 " id " : " body " ,
29 " type " : " object " ,
30 " description " : " Availability check request " ,
31 " properties " : [
Page 13
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
```
32 {
```
33 " id " : " preferred_time " ,
34 " type " : " string " ,
35 " value_type " : " llm_prompt " ,
```
36 " description " : " Time to check ( HH : MM format ) " ,
```
37 " dynamic_variable " : " " ,
38 " constant_value " : " " ,
39 " enum " : null ,
40 " is_system_provided " : false ,
41 " required " : true
```
42 } ,
```
```
43 {
```
44 " id " : " preferred_date " ,
45 " type " : " string " ,
46 " value_type " : " llm_prompt " ,
```
47 " description " : " Date to check ( YYYY - MM - DD format ) " ,
```
48 " dynamic_variable " : " " ,
49 " constant_value " : " " ,
50 " enum " : null ,
51 " is_system_provided " : false ,
52 " required " : true
```
53 } ,
```
```
54 {
```
55 " id " : " doctor_name " ,
56 " type " : " string " ,
57 " value_type " : " llm_prompt " ,
```
58 " description " : " Doctor name ( Hamza , Sara , or Ahmed ) " ,
```
59 " dynamic_variable " : " " ,
60 " constant_value " : " " ,
61 " enum " : [
62 " Hamza " ,
63 " Sara " ,
64 " Ahmed "
65 ] ,
Page 14
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
66 " is_system_provided " : false ,
67 " required " : true
```
68 }
```
69 ] ,
70 " required " : false ,
71 " value_type " : " llm_prompt "
```
72 } ,
```
73 " request_headers " : [
```
74 {
```
75 " type " : " value " ,
76 " name " : " Content - Type " ,
77 " value " : " application / json "
```
78 }
```
79 ] ,
80 " auth_connection " : null
```
81 } ,
```
82 " response_timeout_secs " : 1 0 ,
```
83 " dynamic_variables " : {
```
```
84 " dynami c_ variable_placeholders " : { }
```
```
85 }
```
```
86 }
```
This configuration defines the webhook integration between ElevenLabs and the Make.com
```
workflow, mapping response values to dynamic variables (is_available and availability_message)
```
that can be used in subsequent chatbot interactions. The 10-second timeout ensures re-
sponsive user experience while allowing sufficient time for calendar queries.
2.2.3 Book Appointment Tool
The Book Appointment tool creates confirmed appointments after availability verifica-
tion. Configuration includes:
• Required Parameters:
– Patient full name and date of birth
– Phone number and symptoms/reason for visit
Page 15
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
– Preferred date and time
– Doctor selection and specialty
– Calendar identifier
• Response Mapping:
```
– booking_success (boolean): Whether booking succeeded
```
```
– booking_confirmation (string): Confirmation message
```
```
– event_link (string): Google Calendar event URL
```
• Validation Rules: Data format validation and completeness checks
• Confirmation Workflow: Natural language confirmation before booking
Figure ?? displays the complete tool configuration.
2.2.4 Book Appointment Tool Configuration
The JSON configuration for the Book Appointment tool that creates confirmed appoint-
ments in the appropriate doctor’s calendar is shown below:
Listing 2.2: Book Appointment tool configuration showing complete parameter set and
response mapping
```
1 {
```
2 " type " : " webhook " ,
3 " name " : " Book_Appointment_ 3 _Doctors " ,
4 " description " : " Production booking system for 3 specialized
doctors " ,
5 " disable_interruptions " : true ,
6 " force_pre_tool_speech " : " auto " ,
7 " assignments " : [
```
8 {
```
9 " source " : " response " ,
10 " dynamic_variable " : " patient_name " ,
11 " value_path " : " patient_name "
```
12 } ,
```
Page 16
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
```
13 {
```
14 " source " : " response " ,
15 " dynamic_variable " : " date_of_birth " ,
16 " value_path " : " date_of_birth "
```
17 } ,
```
```
18 {
```
19 " source " : " response " ,
20 " dynamic_variable " : " phone_number " ,
21 " value_path " : " phone_number "
```
22 } ,
```
```
23 {
```
24 " source " : " response " ,
25 " dynamic_variable " : " doctor_name " ,
26 " value_path " : " doctor_name "
```
27 } ,
```
```
28 {
```
29 " source " : " response " ,
30 " dynamic_variable " : " preferred_date " ,
31 " value_path " : " preferred_date "
```
32 } ,
```
```
33 {
```
34 " source " : " response " ,
35 " dynamic_variable " : " preferred_time " ,
36 " value_path " : " preferred_time "
```
37 }
```
38 ] ,
39 " tool_call_sound " : null ,
40 " tool_call_sound_behavior " : " auto " ,
41 " execution_mode " : " immediate " ,
```
42 " api_schema " : {
```
43 " url " : " https : // hook . eu2 . make . com /
d4 w 6 8 e4 c h x n98r39ra49802rv27cwyeu " ,
44 " method " : " POST " ,
45 " path_params_schema " : [ ] ,
Page 17
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
46 " query_params_schema " : [ ] ,
```
47 " request_body_schema " : {
```
48 " id " : " body " ,
49 " type " : " object " ,
50 " description " : " Complete appointment booking data " ,
51 " properties " : [
```
52 {
```
53 " id " : " preferred_time " ,
54 " type " : " string " ,
55 " value_type " : " llm_prompt " ,
56 " description " : " Patient ’ s preferred appointment time
in HH : MM format " ,
57 " dynamic_variable " : " " ,
58 " constant_value " : " " ,
59 " enum " : null ,
60 " is_system_provided " : false ,
61 " required " : true
```
62 } ,
```
```
63 {
```
64 " id " : " language " ,
65 " type " : " string " ,
66 " value_type " : " llm_prompt " ,
```
67 " description " : " User ’ s communication language ( en / ar ) "
```
,
68 " dynamic_variable " : " " ,
69 " constant_value " : " " ,
70 " enum " : [
71 " en " ,
72 " ar "
73 ] ,
74 " is_system_provided " : false ,
75 " required " : true
```
76 } ,
```
```
77 {
```
Page 18
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
78 " id " : " phone_number " ,
79 " type " : " string " ,
80 " value_type " : " llm_prompt " ,
81 " description " : " Patient ’ s contact phone number with
country code " ,
82 " dynamic_variable " : " " ,
83 " constant_value " : " " ,
84 " enum " : null ,
85 " is_system_provided " : false ,
86 " required " : true
```
87 } ,
```
```
88 {
```
89 " id " : " date_of_birth " ,
90 " type " : " string " ,
91 " value_type " : " llm_prompt " ,
92 " description " : " Patient ’ s date of birth in YYYY - MM - DD
format " ,
93 " dynamic_variable " : " " ,
94 " constant_value " : " " ,
95 " enum " : null ,
96 " is_system_provided " : false ,
97 " required " : true
```
98 } ,
```
```
99 {
```
100 " id " : " preferred_date " ,
101 " type " : " string " ,
102 " value_type " : " llm_prompt " ,
103 " description " : " Patient ’ s preferred appointment date
in YYYY - MM - DD format " ,
104 " dynamic_variable " : " " ,
105 " constant_value " : " " ,
106 " enum " : null ,
107 " is_system_provided " : false ,
108 " required " : true
Page 19
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
```
109 } ,
```
```
110 {
```
111 " id " : " doctor_specialty " ,
112 " type " : " string " ,
113 " value_type " : " llm_prompt " ,
114 " description " : " Doctor ’ s medical specialty " ,
115 " dynamic_variable " : " " ,
116 " constant_value " : " " ,
117 " enum " : [
118 " Cardiology " ,
119 " Dermatology " ,
120 " Gastroenterology "
121 ] ,
122 " is_system_provided " : false ,
123 " required " : true
```
124 } ,
```
```
125 {
```
126 " id " : " patient_name " ,
127 " type " : " string " ,
128 " value_type " : " llm_prompt " ,
129 " description " : " Patient ’ s complete legal name " ,
130 " dynamic_variable " : " " ,
131 " constant_value " : " " ,
132 " enum " : null ,
133 " is_system_provided " : false ,
134 " required " : true
```
135 } ,
```
```
136 {
```
137 " id " : " calendar_id " ,
138 " type " : " string " ,
139 " value_type " : " llm_prompt " ,
140 " description " : " Google Calendar ID corresponding to
selected doctor " ,
141 " dynamic_variable " : " " ,
Page 20
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
142 " constant_value " : " " ,
143 " enum " : null ,
144 " is_system_provided " : false ,
145 " required " : true
```
146 } ,
```
```
147 {
```
148 " id " : " symptoms_reason " ,
149 " type " : " string " ,
150 " value_type " : " llm_prompt " ,
151 " description " : " Primary reason for visit or main
symptoms " ,
152 " dynamic_variable " : " " ,
153 " constant_value " : " " ,
154 " enum " : null ,
155 " is_system_provided " : false ,
156 " required " : true
```
157 } ,
```
```
158 {
```
159 " id " : " doctor_name " ,
160 " type " : " string " ,
161 " value_type " : " llm_prompt " ,
```
162 " description " : " Selected doctor name ( Hamza , Sara , or
```
```
Ahmed ) " ,
```
163 " dynamic_variable " : " " ,
164 " constant_value " : " " ,
165 " enum " : [
166 " Hamza " ,
167 " Sara " ,
168 " Ahmed "
169 ] ,
170 " is_system_provided " : false ,
171 " required " : true
```
172 }
```
173 ] ,
Page 21
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
174 " required " : false ,
175 " value_type " : " llm_prompt "
```
176 } ,
```
177 " request_headers " : [
```
178 {
```
179 " type " : " value " ,
180 " name " : " Content - Type " ,
181 " value " : " application / json "
```
182 }
```
183 ] ,
184 " auth_connection " : null
```
185 } ,
```
186 " response_timeout_secs " : 2 0 ,
```
187 " dynamic_variables " : {
```
```
188 " dynami c_ variable_placeholders " : { }
```
```
189 }
```
```
190 }
```
This configuration defines the booking tool that creates confirmed appointments after
availability verification. The tool collects comprehensive patient information including
name, contact details, medical symptoms, and scheduling preferences. Note the 20-
```
second response timeout (longer than the availability check tool) to accommodate the
```
more complex booking process. The language parameter enables multilingual support
```
(English/Arabic) for confirmation messages, while the calendar_id parameter ensures
```
appointments are created in the correct specialist’s calendar. All response values are
mapped to dynamic variables for use in subsequent chatbot interactions and confirmation
messages.
2.3 Dynamic Variables and Testing
ElevenLabs requires dynamic variable placeholders for development testing. The following
variables were configured:
Page 22
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
Figure 2.2: Dynamic variable configuration for development testing
Test values used during development:
• is_available: true
• availability_message: "The slot is free."
• booking_success: true
• booking_confirmation: "Appointment confirmed successfully."
• event_link: "https://calendar.google.com/calendar/event?eid=test123"
These values were used to simulate successful interactions during prompt development
and testing before connecting to the live Make.com workflows.
2.4 Language Switching Implementation
The chatbot implements automatic language detection and switching between English
and Arabic. The system prompt includes specific rules:
• Mirror the user’s language exactly for all responses
• Switch languages seamlessly if the user changes language mid-conversation
• Maintain clinical accuracy and safety protocols regardless of language
Page 23
Clinical Chatbot System CHAPTER 2. CHATBOT CONFIGURATION
• Provide equivalent medical terminology in both languages
Figure 2.3 shows the language detection workflow within the chatbot logic.
Figure 2.3: Language detection and switching workflow showing automatic language
mirroring
Testing confirmed successful language switching between English and Arabic during
patient interactions.
Page 24
Chapter 3
Workflow Implementation
3.1 Workflow Architecture
The Make.com workflows handle the business logic between the ElevenLabs chatbot and
Google Calendar. Two primary workflows were implemented:
Figure 3.1: Complete workflow architecture showing both availability check and booking
workflows
• Check Availability Workflow: Verifies doctor availability before booking
• Book Appointment Workflow: Creates confirmed appointments in the appro-
priate calendar
Both workflows share a common structure of webhook triggers, router modules for
doctor selection, Google Calendar integration, and response generation.
25
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
3.2 Availability Check Workflow
The availability check workflow follows these steps:
1. Webhook Trigger: Receives request from ElevenLabs with doctor name, date,
and time
2. Router Module: Routes to the appropriate doctor’s calendar based on name
3. Google Calendar Query: Lists events for the specified date using the calendar
ID
4. Availability Logic: Checks if the preferred time slot is occupied
5. Response Generation: Returns availability status and appropriate message
Figure 3.2 illustrates the complete workflow diagram.
Page 26
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
Figure 3.2: Availability check workflow showing router structure and calendar query logic
3.2.1 Router Configuration
The router module contains three routes, one for each doctor:
Page 27
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
• Route 1: Doctor name equals "Hamza" Cardiology calendar
• Route 2: Doctor name equals "Sara" Dermatology calendar
• Route 3: Doctor name equals "Ahmed" Gastroenterology calendar
Figure 3.3 shows the router setup with condition definitions.
Figure 3.3: Router configuration showing condition setup for three doctors
3.2.2 Google Calendar Module Setup
Each route contains a Google Calendar module configured to:
• Connection: Use the authenticated Google account with access to all three cal-
endars
• Calendar Selection: Dynamically select the calendar ID based on router output
• Time Range: Set from 00:00 to 23:59 on the requested date
• Event Filtering: Retrieve all events for conflict checking
Figure 3.4 displays the Google Calendar module configuration.
Page 28
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
Figure 3.4: Google Calendar module configuration showing time range and calendar
selection
3.2.3 Availability Logic Implementation
The availability logic checks if the preferred time slot conflicts with existing events:
```
• Event Count Check: length(Search_Events.events) = 0 indicates no con-
```
flicts
• Time Slot Verification: Exact time matching for precision
• Response Generation: Binary true/false response with appropriate message
Figure 3.5 shows the variable setup and response generation logic.
Page 29
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
Figure 3.5: Availability logic showing event count check and response generation
3.3 Booking Workflow Implementation
The appointment booking workflow executes after availability confirmation:
1. Webhook Trigger: Receives complete booking details from ElevenLabs
2. Router Module: Routes to the correct doctor’s calendar
3. Event Creation: Creates Google Calendar event with all patient details
4. Confirmation Generation: Builds success message with calendar link
5. Error Handling: Manages failures with appropriate fallback messages
Figure 3.6 illustrates the complete booking workflow.
Page 30
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
Figure 3.6: Booking workflow showing event creation and confirmation logic
3.3.1 Event Creation Configuration
The Google Calendar event creation module is configured with:
• Event Title: "Appointment - [Patient Name]"
• Description: Structured patient details including:
– Patient name and date of birth
– Phone number and symptoms
– Doctor specialty and reason for visit
• Start/End Time: 30-minute appointment slots based on preferred time
Page 31
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
• Attendees: Clinic email address for notifications
• Reminders: 24-hour and 1-hour email reminders
Figure 3.7 displays the event creation configuration.
Figure 3.7: Event creation configuration showing title, description, and timing setup
3.4 Error Handling and Recovery
Comprehensive error handling was implemented for system reliability:
Page 32
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
Figure 3.8: Error handling workflow showing fallback procedures and user notifications
3.4.1 Common Error Scenarios
The system handles several error scenarios:
• Calendar Access Errors: Fallback to manual booking suggestion
• Time Conflicts: Slot may be taken between availability check and booking
• Invalid Input: Date format validation and phone number verification
• System Timeouts: Retry logic with user-friendly error messages
• Connection Failures: Graceful degradation with alternative contact methods
3.4.2 Recovery Procedures
For each error scenario, specific recovery procedures were implemented:
Page 33
Clinical Chatbot System CHAPTER 3. WORKFLOW IMPLEMENTATION
• Immediate Feedback: Clear error messages to users
• Alternative Suggestions: Recommend different times or specialists
• Human Escalation: Provide contact information for manual assistance
• Logging: Detailed error logging for system improvement
Figure 3.9 shows the error recovery workflow.
Figure 3.9: Error recovery procedures showing fallback options and escalation paths
The Make.com workflows provide a robust, reliable foundation for the chatbot system,
ensuring seamless integration between conversational AI and calendar management while
maintaining clinical safety and operational efficiency.
Page 34
Chapter 4
Google Integration
4.1 Calendar Configuration
The system integrates with three separate Google Calendars, one for each specialist.
Figure 4.1 shows the calendar configuration within Google Calendar.
Figure 4.1: Google Calendar setup showing three separate calendars for Cardiology, Der-
matology, and Gastroenterology
```
4.1.1 Cardiology Calendar (Dr. Hamza)
```
Calendar ID: dr.hamza@clinic.com
Specialty Coverage:
35
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
• Heart, chest pain, palpitations
• Shortness of breath, high blood pressure
• Circulation problems, leg swelling
• General cardiovascular concerns
The calendar is configured with:
• Working hours: Monday-Friday, 8:00 AM to 5:00 PM Egypt time
• 30-minute appointment slots
• Buffer time between appointments for preparation
• Shared access permissions for the Make.com service account
```
4.1.2 Dermatology Calendar (Dr. Sara)
```
Calendar ID: dr.sara@clinic.com
Specialty Coverage:
• Skin rashes, acne, itching, redness
• Hair loss, eczema, psoriasis
• Fungal infections, allergic skin reactions
The calendar is configured with:
• Working hours: Monday-Friday, 8:00 AM to 5:00 PM Egypt time
• 30-minute appointment slots
• Buffer time between appointments for preparation
• Shared access permissions for the Make.com service account
Page 36
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
```
4.1.3 Gastroenterology Calendar (Dr. Ahmed)
```
Calendar ID: dr.ahmed@clinic.com
Specialty Coverage:
• Stomach pain, nausea, vomiting
• Diarrhea, constipation, bloating
• GERD, digestive issues, liver-related symptoms
The calendar is configured with:
• Working hours: Monday-Friday, 8:00 AM to 5:00 PM Egypt time
• 30-minute appointment slots
• Buffer time between appointments for preparation
• Shared access permissions for the Make.com service account
4.2 Time Zone Configuration
A critical aspect of the implementation was ensuring proper time zone handling for Egyp-
tian time. Figure 4.2 shows the time zone settings.
```
Figure 4.2: Time zone configuration showing Egyptian time zone (Africa/Cairo) settings
```
Page 37
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
4.2.1 Egyptian Time Synchronization
The system leverages Google Calendar’s built-in timestamp features to maintain accurate
Egyptian time:
• Time Zone Setting: All calendars configured to Africa/Cairo time zone
• Automatic DST Handling: Google Calendar automatically adjusts for daylight
saving time
• Real-Time Synchronization: Current time derived from Google Calendar API
responses
```
• Timestamp Format: ISO 8601 format with time zone offset (+02:00 for Egypt)
```
Figure 4.3 illustrates how current time is extracted from Google Calendar responses.
Figure 4.3: Timestamp extraction showing how current Egyptian time is derived from
calendar responses
4.2.2 Time Validation Logic
The system includes comprehensive time validation to prevent invalid bookings:
• Past Date Prevention: Blocks appointments for dates before current date
Page 38
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
• Working Hours Enforcement: Restricts bookings to 8:00 AM - 5:00 PM Monday-
Friday
• Time Format Validation: Ensures HH:MM format for all time inputs
• Slot Availability Checking: Verifies no overlapping appointments
Figure 4.4 shows the time validation logic implementation.
Figure 4.4: Time validation logic showing past date prevention and working hours en-
forcement
4.3 Event Management
The system creates and manages Google Calendar events with specific formatting and
content requirements. Figure ?? shows the event management workflow.
Page 39
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
```
(a) Event creation process ask-
```
ing patient details
```
(b) Ask for the reason and the
```
```
preferred doctor (c) Confirm Booking
```
Figure 4.5: Complete event management workflow
When a booking is confirmed, the following event details are created:
• Title: "Appointment - [Patient Name]"
• Description:
```
Patient: [Patient Name]
```
```
DOB: [Date of Birth]
```
```
Phone: [Phone Number]
```
```
Reason: [Symptoms/Reason]
```
```
Specialty: [Doctor Specialty]
```
```
Doctor: [Doctor Name]
```
• Start Time: [Preferred Date]T[Preferred Time]:00+02:00
• End Time: [Preferred Date]T[Preferred Time + 30 minutes]:00+02:00
• Attendees: clinic@clinic.com
```
• Reminders: 1440 minutes (24 hours) and 60 minutes (1 hour) before appointment
```
Figure 4.6 displays a sample calendar event.
Page 40
Clinical Chatbot System CHAPTER 4. GOOGLE INTEGRATION
Figure 4.6: Sample calendar event showing patient details and appointment information
Page 41
Chapter 5
Safety Implementation
5.1 Red-Flag Symptom Detection
The chatbot includes comprehensive red-flag symptom detection logic to identify emer-
gency situations requiring immediate attention. Figure 5.1 illustrates the detection work-
flow.
Figure 5.1: Red-flag symptom detection workflow showing emergency protocol activation
42
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
5.1.1 Cardiology Red Flags
The system detects the following cardiology emergency symptoms:
• Severe chest pain: Crushing, pressure-like, or radiating to arm/jaw
• Shortness of breath: Sudden onset, at rest, or with minimal exertion
• Syncope: Fainting or loss of consciousness
• Palpitations: Rapid, irregular heartbeat with dizziness
When detected, the system immediately:
• Stops all booking processes
• Instructs the user to seek emergency care
• Provides clear emergency instructions
• Does not proceed with availability checks or booking
Figure 5.2 shows the emergency response for cardiology red flags.
Page 43
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
Figure 5.2: Cardiology emergency response showing immediate escalation protocol
5.1.2 Dermatology Red Flags
The system detects the following dermatology emergency symptoms:
• Rapidly spreading rash: With fever or systemic symptoms
• Facial swelling: Especially around eyes, lips, or tongue
• Severe blistering: Over large body areas or mucous membranes
• Skin infections: With fever, redness, warmth, or pus
Emergency response includes:
• Immediate interruption of normal workflow
• Clear instructions to seek emergency care
Page 44
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
• Explanation of why this requires immediate attention
• No attempt to book routine appointments
5.1.3 Gastroenterology Red Flags
The system detects the following gastroenterology emergency symptoms:
• Vomiting blood: Bright red or coffee-ground appearance
• Black/tarry stools: Indicating gastrointestinal bleeding
• Severe abdominal pain: With fever, vomiting, or inability to keep fluids down
• Jaundice: Yellow skin/eyes with abdominal pain
Emergency protocol activation:
• Complete workflow interruption
• Direct emergency care instructions
• No appointment booking attempts
• Clear explanation of urgency
5.2 Specialty Routing Logic
The system implements strict specialty separation to ensure patients are routed to the
correct specialist. Figure 5.3 shows the routing logic.
Page 45
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
Figure 5.3: Specialty routing logic showing symptom-based assignment to appropriate
specialists
```
5.2.1 Cardiology Routing (Dr. Hamza)
```
Symptoms mapped to Cardiology:
• Heart pain, chest discomfort, palpitations
```
• Shortness of breath (non-asthmatic), high blood pressure
```
• Circulation problems, leg swelling, cardiovascular concerns
The routing logic ensures:
Page 46
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
• Exclusive assignment: Symptoms only match one specialty
• No overlap: Clear boundaries between specialties
• User override: Patient can choose different specialist if preferred
• Default assignment: Automatic routing when symptoms clearly match
```
5.2.2 Dermatology Routing (Dr. Sara)
```
Symptoms mapped to Dermatology:
• Skin rashes, acne, itching, redness, hair loss
• Eczema, psoriasis, fungal infections, allergic reactions
Routing rules include:
• Skin-focused symptoms: Only dermatological conditions
• No internal symptoms: External presentation only
• Clear symptom boundaries: Distinct from other specialties
• Patient choice: User can override system suggestion
```
5.2.3 Gastroenterology Routing (Dr. Ahmed)
```
Symptoms mapped to Gastroenterology:
• Stomach pain, nausea, vomiting, diarrhea, constipation
• Bloating, GERD, digestive issues, liver-related symptoms
Routing logic ensures:
• Digestive system focus: Only gastrointestinal symptoms
• No cardiac overlap: Clear separation from chest pain
• Systematic approach: Organized symptom mapping
• Safety first: Red flags take precedence over routing
Page 47
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
5.3 Safety Guardrails
Comprehensive safety guardrails were implemented to prevent inappropriate medical ad-
vice. Figure 5.4 shows the guardrail implementation.
Figure 5.4: Safety guardrails showing prohibited actions and emergency override protocols
5.3.1 Prohibited Actions
The system is explicitly prohibited from:
• Diagnosis: Never provides specific medical diagnoses
• Treatment: Never recommends specific treatments or medications
• Prognosis: Never predicts disease outcomes or progression
Page 48
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
• Second opinions: Never comments on previous medical advice
• Emergency handling: Only provides emergency instructions, not treatment
5.3.2 Permitted Actions
The system is allowed to:
• Triage: Assess symptom severity and urgency
• Routing: Direct to appropriate specialists
• Education: Provide general health information from authoritative sources
• Scheduling: Book appointments with appropriate providers
• Emergency guidance: Instruct to seek immediate care when needed
5.3.3 Source Citation Requirements
When providing health information, the system must cite authoritative sources:
• MedlinePlus: For patient education materials
• WHO Guidelines: For international health standards
• ICD-10: For condition classification and coding
• Clinical Guidelines: From recognized medical organizations
Figure 5.5 shows the citation implementation in responses.
Page 49
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
Figure 5.5: Source citation implementation showing proper attribution in patient re-
sponses
5.4 Testing and Validation
The clinical safety features were rigorously tested with common scenarios. Figure ??
shows the testing methodology.
5.4.1 Test Cases
Validated clinical scenarios:
• Chest pain: Successfully identified red-flag symptoms and routed to emergency
care
• Skin rash: Correctly assigned to Dermatology with appropriate triage questions
• Severe headache: Properly assessed for emergency indicators and routed appro-
priately
• Stomach pain: Correctly identified as Gastroenterology case with proper follow-
up
Page 50
Clinical Chatbot System CHAPTER 5. SAFETY IMPLEMENTATION
5.4.2 Edge Case Handling
Challenging scenarios tested:
• Mixed symptoms: Chest pain with skin rash - system prioritized cardiac emer-
gency
• Vague descriptions: "I don’t feel well" - system asked clarifying questions
• Medical jargon: Patient used technical terms - system maintained appropriate
boundaries
• Language switching: Arabic/English mixed conversation - system maintained
safety protocols
The clinical safety implementation ensures that the chatbot system maintains the
highest standards of patient safety while providing valuable triage and appointment
services. The combination of red-flag detection, specialty routing, and comprehensive
guardrails creates a system that is both clinically responsible and operationally effec-
tive.
Page 51