from app.core.database import SessionLocal, Base, engine
from app.models.models import Scheme, EligibilityRule, SchemeDocument, ApplicationStep, SavedScheme, Notification


def seed_schemes():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Remove prior seed data so the script is idempotent
    db.query(ApplicationStep).delete()
    db.query(SchemeDocument).delete()
    db.query(EligibilityRule).delete()
    db.query(SavedScheme).delete()
    db.query(Notification).delete()
    db.query(Scheme).delete()

    sample_schemes = [
        # 1. PM Scholarship Scheme
        {
            "title": "PM Scholarship Scheme (PMSS)",
            "department": "Ministry of Education & Welfare",
            "description": "Financial assistance for meritorious students from low-income and dependent families to pursue technical and higher education courses (Engineering, Medical, MBA, etc.).",
            "benefits": "Up to Rs. 50,000 per year for male students and Rs. 54,000 per year for female students for tuition and living costs.",
            "category": "Education",
            "target_group": "Students",
            "state": "All India",
            "official_link": "https://scholarships.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "is_student", "operator": "eq", "value": "true", "description": "Applicant must be a currently enrolled student"},
                {"field_name": "income", "operator": "lte", "value": "300000", "description": "Family annual income must be Rs. 3,00,000 or below"},
                {"field_name": "age", "operator": "lte", "value": "25", "description": "Applicant age must be 25 years or below"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Income Certificate", "is_mandatory": True},
                {"document_name": "Marksheet of Last Qualifying Exam (min 60%)", "is_mandatory": True},
                {"document_name": "College Admission Confirmation / Fee Receipt", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Register on the National Scholarship Portal (NSP) at scholarships.gov.in."},
                {"step_number": 2, "instruction": "Select PMSS Scheme and fill in academic, bank, and income details."},
                {"step_number": 3, "instruction": "Upload verified marksheets and get verification from your college nodal officer."},
                {"step_number": 4, "instruction": "Submit application before deadline and track DBT disbursement."},
            ],
        },

        # 2. PM-KISAN Samman Nidhi
        {
            "title": "PM-KISAN Samman Nidhi",
            "department": "Ministry of Agriculture & Farmers Welfare",
            "description": "Direct income support to all landholding farmer families across the country to supplement their financial needs for agricultural inputs and domestic requirements.",
            "benefits": "Rs. 6,000 per year provided in three equal 4-monthly installments of Rs. 2,000 directly into the farmer's Aadhaar-linked bank account.",
            "category": "Agriculture",
            "target_group": "Farmers",
            "state": "All India",
            "official_link": "https://pmkisan.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "is_farmer", "operator": "eq", "value": "true", "description": "Applicant must be an active farmer"},
                {"field_name": "income", "operator": "lte", "value": "250000", "description": "Modest income farming family (Non-institutional landholders)"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card with linked mobile number", "is_mandatory": True},
                {"document_name": "Land Ownership Record (Patta/Khatoni)", "is_mandatory": True},
                {"document_name": "Active Bank Account Passbook (Aadhaar seeded)", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit pmkisan.gov.in or nearest Common Service Centre (CSC)."},
                {"step_number": 2, "instruction": "Click 'New Farmer Registration' and enter Aadhaar and State details."},
                {"step_number": 3, "instruction": "Enter land khata numbers, bank details and complete e-KYC via Aadhaar OTP."},
                {"step_number": 4, "instruction": "State Nodal Officer approves the application for direct DBT disbursement."},
            ],
        },

        # 3. Ayushman Bharat - PM-JAY
        {
            "title": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
            "department": "National Health Authority (Ministry of Health)",
            "description": "World's largest government-funded healthcare assurance scheme providing comprehensive health cover for secondary and tertiary hospital care.",
            "benefits": "Cashless health insurance cover up to Rs. 5,00,000 per family per year for over 1,900 medical and surgical procedures across empanelled public and private hospitals.",
            "category": "Healthcare",
            "target_group": "Low Income Families",
            "state": "All India",
            "official_link": "https://pmjay.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "income", "operator": "lte", "value": "250000", "description": "Annual household income must be Rs. 2,50,000 or below (SECC identified)"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card or Ration Card", "is_mandatory": True},
                {"document_name": "Income Certificate / SECC identification", "is_mandatory": True},
                {"document_name": "Family Member ID Proof", "is_mandatory": False},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Check your family eligibility at pmjay.gov.in using your mobile number or Ration Card."},
                {"step_number": 2, "instruction": "Visit nearest Empanelled Health Care Provider (EHCP) or CSC centre."},
                {"step_number": 3, "instruction": "Complete biometric e-KYC with the Ayushman Mitra representative."},
                {"step_number": 4, "instruction": "Download your Ayushman Golden Card for instant cashless treatment."},
            ],
        },

        # 4. Pradhan Mantri Awas Yojana (PMAY)
        {
            "title": "Pradhan Mantri Awas Yojana (PMAY - Housing for All)",
            "department": "Ministry of Housing and Urban Affairs",
            "description": "Subsidized housing and financial assistance for homeless and kutcha-house dwelling families to construct or purchase a pucca house with basic amenities.",
            "benefits": "Direct financial assistance of up to Rs. 1.20 lakh (plains) to Rs. 1.30 lakh (hilly areas) or interest subsidy up to 6.5% on housing loans up to Rs. 2.67 lakh.",
            "category": "Housing",
            "target_group": "Homeless & EWS Families",
            "state": "All India",
            "official_link": "https://pmaymis.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "income", "operator": "lte", "value": "300000", "description": "Economically Weaker Section (EWS) or Low Income Group (LIG)"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card of all family members", "is_mandatory": True},
                {"document_name": "Income Proof / BPL Certificate", "is_mandatory": True},
                {"document_name": "Land title or NOC for construction site", "is_mandatory": True},
                {"document_name": "Bank Account Details", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Apply online at pmaymis.gov.in or through local Gram Panchayat / Urban Local Body."},
                {"step_number": 2, "instruction": "Enter Aadhaar verification and declare household income details."},
                {"step_number": 3, "instruction": "Physical geo-tagged site inspection conducted by municipal surveyors."},
                {"step_number": 4, "instruction": "Direct stage-wise fund transfer into bank account upon construction milestones."},
            ],
        },

        # 5. Mahila Samman Savings Certificate
        {
            "title": "Mahila Samman Savings Certificate",
            "department": "Ministry of Finance",
            "description": "Small savings scheme exclusively for women and girl children to encourage financial independence, high savings yields, and asset accumulation.",
            "benefits": "Fixed guaranteed 7.5% annual interest rate compounded quarterly on deposits up to Rs. 2,00,000 for a 2-year maturity tenure with partial withdrawal facility.",
            "category": "Women Welfare",
            "target_group": "Women & Girls",
            "state": "All India",
            "official_link": "https://financialservices.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "gender", "operator": "eq", "value": "female", "description": "Open exclusively to female citizens or girl children through guardians"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card of applicant", "is_mandatory": True},
                {"document_name": "PAN Card", "is_mandatory": False},
                {"document_name": "2 Passport Size Photographs", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit your nearest Post Office or authorized Public Sector Bank branch."},
                {"step_number": 2, "instruction": "Obtain and fill Form 1 (Application for opening Mahila Samman account)."},
                {"step_number": 3, "instruction": "Deposit amount (min Rs. 1,000 to max Rs. 2,00,000) via Cash or Cheque."},
                {"step_number": 4, "instruction": "Receive physical passbook and Certificate of Deposit."},
            ],
        },

        # 6. Sukanya Samriddhi Yojana (SSY)
        {
            "title": "Sukanya Samriddhi Yojana (SSY - Beti Bachao Beti Padhao)",
            "department": "Ministry of Finance & Women Child Development",
            "description": "Government-backed savings scheme for parents of girl children to build a dedicated education and marriage fund with highest interest rate and Section 80C tax exemption.",
            "benefits": "Attractive 8.2% annual compound interest rate, 100% tax-free maturity returns, and deposit limit from Rs. 250 to Rs. 1.5 Lakh per financial year.",
            "category": "Women Welfare",
            "target_group": "Girl Children (Parents)",
            "state": "All India",
            "official_link": "https://www.indiapost.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "gender", "operator": "eq", "value": "female", "description": "Account opened in the name of the girl child"},
                {"field_name": "age", "operator": "lte", "value": "10", "description": "Girl child must be below 10 years of age at the time of opening"},
            ],
            "documents": [
                {"document_name": "Birth Certificate of the Girl Child", "is_mandatory": True},
                {"document_name": "Aadhaar Card of Parent / Guardian", "is_mandatory": True},
                {"document_name": "Address Proof & Photos", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit any Post Office or commercial bank (SBI, PNB, Canara, etc.)."},
                {"step_number": 2, "instruction": "Fill SSY Account Opening Form with details of the girl child and parent."},
                {"step_number": 3, "instruction": "Deposit minimum initial amount of Rs. 250."},
                {"step_number": 4, "instruction": "Account matures after 21 years or on marriage after attaining age 18."},
            ],
        },

        # 7. PM Mudra Yojana (PMMY)
        {
            "title": "Pradhan Mantri Mudra Yojana (PMMY - Micro Loans)",
            "department": "Ministry of Finance (Dept. of Financial Services)",
            "description": "Collateral-free institutional loans for non-corporate, non-farm small/micro enterprises and aspiring entrepreneurs in manufacturing, trading, and services.",
            "benefits": "Collateral-free loans up to Rs. 10 Lakh (Shishu: up to Rs. 50k, Kishore: Rs. 50k - 5 Lakh, Tarun: Rs. 5 Lakh - 10 Lakh) with affordable interest rates.",
            "category": "Employment & Business",
            "target_group": "Entrepreneurs & Self-Employed",
            "state": "All India",
            "official_link": "https://www.mudra.org.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be at least 18 years old"},
                {"field_name": "occupation", "operator": "in", "value": "self-employed,salaried,unemployed", "description": "Open to existing and new micro-business owners"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card & PAN Card", "is_mandatory": True},
                {"document_name": "Business Enterprise Proof / Udyam Registration", "is_mandatory": False},
                {"document_name": "Bank statement for past 6 months", "is_mandatory": True},
                {"document_name": "Quotations / Project Report for machinery or working capital", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Prepare business plan and identify loan category (Shishu, Kishore, or Tarun)."},
                {"step_number": 2, "instruction": "Apply online on the Udyamimitra portal (udyamimitra.in) or visit nearest bank."},
                {"step_number": 3, "instruction": "Submit identity, business quotation, and KYC documents."},
                {"step_number": 4, "instruction": "Receive Mudra Debit Card upon loan sanction for working capital withdrawals."},
            ],
        },

        # 8. PM SVANidhi
        {
            "title": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
            "department": "Ministry of Housing and Urban Affairs",
            "description": "Micro-credit facility to empower urban and peri-urban street vendors to resume their livelihoods and scale their small businesses.",
            "benefits": "Initial working capital loan of Rs. 10,000, progressing to Rs. 20,000 and Rs. 50,000 upon timely repayment, with 7% interest subsidy and cashback on digital transactions.",
            "category": "Employment & Business",
            "target_group": "Street Vendors & Small Traders",
            "state": "All India",
            "official_link": "https://pmsvanidhi.mohua.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be aged 18 years or above"},
                {"field_name": "occupation", "operator": "in", "value": "self-employed,unemployed", "description": "Street vending in urban or semi-urban areas"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Vending Certificate / Urban Local Body Identity Card", "is_mandatory": True},
                {"document_name": "Bank Passbook with UPI enabled", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit pmsvanidhi.mohua.gov.in or download the PM SVANidhi Mobile App."},
                {"step_number": 2, "instruction": "Verify your mobile number with Aadhaar OTP and check vending certificate status."},
                {"step_number": 3, "instruction": "Choose your preferred lending institution (Lender)."},
                {"step_number": 4, "instruction": "Loan disbursed directly into savings account within 7 to 10 days."},
            ],
        },

        # 9. PM Vishwakarma Scheme
        {
            "title": "PM Vishwakarma Scheme (Support for Traditional Artisans)",
            "department": "Ministry of Micro, Small and Medium Enterprises",
            "description": "End-to-end holistic support for traditional artisans and craftspeople across 18 traditional trades (Carpenters, Blacksmiths, Tailors, Potters, Cobblers, Sculptors, etc.).",
            "benefits": "PM Vishwakarma Certificate & ID Card, skill upgradation training with Rs. 500/day stipend, Rs. 15,000 toolkit grant, and collateral-free loans up to Rs. 3 Lakh at subsidized 5% interest.",
            "category": "Employment & Business",
            "target_group": "Artisans & Craftsmen",
            "state": "All India",
            "official_link": "https://pmvishwakarma.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be at least 18 years of age"},
                {"field_name": "occupation", "operator": "in", "value": "self-employed,unemployed", "description": "Practicing one of the 18 traditional trade crafts"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card and Mobile Number", "is_mandatory": True},
                {"document_name": "Bank Account Passbook", "is_mandatory": True},
                {"document_name": "Ration Card (Family declaration)", "is_mandatory": True},
                {"document_name": "Trade verification certificate / Gram Panchayat recommendation", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Register at nearest Common Service Centre (CSC) with Aadhaar biometric authentication."},
                {"step_number": 2, "instruction": "Trade verification by Gram Panchayat Head or Urban Local Body Head."},
                {"step_number": 3, "instruction": "Attend 5-7 days basic skill training with daily stipend."},
                {"step_number": 4, "instruction": "Receive toolkit e-voucher of Rs. 15,000 and apply for 1st tranche loan of Rs. 1 Lakh."},
            ],
        },

        # 10. National Career Service (NCS)
        {
            "title": "National Career Service (NCS) Portal",
            "department": "Ministry of Labour and Employment",
            "description": "National digital employment exchange connecting job seekers with certified private and government employers, job fairs, internships, and skill training.",
            "benefits": "Free job matching, skill development referrals, free access to career counselling, DigiLocker integration, and direct job fair interview alerts.",
            "category": "Employment & Business",
            "target_group": "Job Seekers & Youth",
            "state": "All India",
            "official_link": "https://ncs.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be at least 18 years old"},
                {"field_name": "occupation", "operator": "in", "value": "unemployed,student,salaried", "description": "Open to all active job aspirants"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Educational Certificates (10th/12th/Degree/Diploma)", "is_mandatory": True},
                {"document_name": "Resume / CV in PDF format", "is_mandatory": False},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit ncs.gov.in and click 'Jobseeker Registration'."},
                {"step_number": 2, "instruction": "Verify via Aadhaar or PAN and build your digital resume profile."},
                {"step_number": 3, "instruction": "Filter jobs by industry, state, work-from-home, and salary expectations."},
                {"step_number": 4, "instruction": "Apply directly with one click and track interview invitations."},
            ],
        },

        # 11. Indira Gandhi National Old Age Pension
        {
            "title": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
            "department": "Ministry of Rural Development (NSAP)",
            "description": "Non-contributory monthly social pension for destitute and senior citizens belonging to below-poverty-line (BPL) households.",
            "benefits": "Monthly financial pension assistance of Rs. 200 - Rs. 500 (with state government top-up up to Rs. 1,000 - Rs. 2,000 in many states) credited directly to bank account.",
            "category": "Senior Citizens",
            "target_group": "Senior Citizens",
            "state": "All India",
            "official_link": "https://nsap.nic.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "60", "description": "Applicant must be aged 60 years or older"},
                {"field_name": "income", "operator": "lte", "value": "150000", "description": "Household income below poverty line (BPL category)"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card / Voter ID (Age proof)", "is_mandatory": True},
                {"document_name": "BPL Ration Card / Income Certificate", "is_mandatory": True},
                {"document_name": "Bank / Post Office Account Passbook", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Obtain the NSAP application form from local Gram Panchayat or Municipal Ward office."},
                {"step_number": 2, "instruction": "Attach age proof, BPL card copy and bank account details."},
                {"step_number": 3, "instruction": "Submit to Block Development Officer (BDO) or Social Welfare Department."},
                {"step_number": 4, "instruction": "Sanctioned pension will be credited monthly via Direct Benefit Transfer (DBT)."},
            ],
        },

        # 12. National Disability Pension Scheme
        {
            "title": "National Disability Pension Scheme (IGNDPS)",
            "department": "Ministry of Social Justice and Empowerment",
            "description": "Monthly disability pension and social security assistance for persons with severe and multiple disabilities living in low-income families.",
            "benefits": "Monthly pension assistance (Rs. 300 to Rs. 1,500 depending on state) plus free distribution of assistive devices (wheelchairs, hearing aids, tri-cycles).",
            "category": "Disability Support",
            "target_group": "Persons with Benchmark Disabilities",
            "state": "All India",
            "official_link": "https://disabilityaffairs.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "has_disability", "operator": "eq", "value": "true", "description": "Applicant must possess a recognized disability certificate"},
                {"field_name": "income", "operator": "lte", "value": "180000", "description": "Low income or BPL household criteria"},
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant age 18 years or above"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Unique Disability ID (UDID) / Disability Certificate (min 40%)", "is_mandatory": True},
                {"document_name": "Income Certificate", "is_mandatory": True},
                {"document_name": "Bank Passbook", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Obtain UDID card from Government District Hospital."},
                {"step_number": 2, "instruction": "Submit IGNDPS application to District Social Welfare Office or online via nsap.nic.in."},
                {"step_number": 3, "instruction": "Verification by Taluk/Block Medical Social Officer."},
                {"step_number": 4, "instruction": "Monthly pension disbursement via Aadhaar Enabled Payment System (AePS)."},
            ],
        },

        # 13. PM Fasal Bima Yojana (PMFBY)
        {
            "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY - Crop Insurance)",
            "department": "Ministry of Agriculture & Farmers Welfare",
            "description": "Comprehensive crop insurance scheme providing financial support to farmers suffering crop loss/damage arising from non-preventable natural calamities, pests, and diseases.",
            "benefits": "Maximum insurance coverage with very low farmer premium rates: only 2% for Kharif crops, 1.5% for Rabi crops, and 5% for annual commercial/horticultural crops with quick claim settlements.",
            "category": "Agriculture",
            "target_group": "Farmers",
            "state": "All India",
            "official_link": "https://pmfby.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "is_farmer", "operator": "eq", "value": "true", "description": "Applicant must be a farmer growing notified crops"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Land Record (RoR / Khasra / Khatoni)", "is_mandatory": True},
                {"document_name": "Sowing Certificate / Declaration from local Village Officer", "is_mandatory": True},
                {"document_name": "Bank Account Passbook", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit pmfby.gov.in portal or nearest CSC / Bank branch before cutoff sowing date."},
                {"step_number": 2, "instruction": "Select state, crop, season (Kharif/Rabi), and acreage sown."},
                {"step_number": 3, "instruction": "Pay the nominal farmer premium online."},
                {"step_number": 4, "instruction": "Report any crop damage within 72 hours via Crop Insurance App for automated surveyor assessment."},
            ],
        },

        # 14. Kisan Credit Card (KCC)
        {
            "title": "Kisan Credit Card (KCC) Scheme",
            "department": "Ministry of Agriculture / RBI & NABARD",
            "description": "Timely and adequate credit support to farmers from the banking system for crop cultivation, post-harvest expenses, and animal husbandry/fisheries needs.",
            "benefits": "Revolving credit limit up to Rs. 3 Lakh at an effective subsidized interest rate of just 4% per annum (with 3% prompt repayment incentive) without collateral for loans up to Rs. 1.60 Lakh.",
            "category": "Agriculture",
            "target_group": "Farmers & Fishermen",
            "state": "All India",
            "official_link": "https://pmkisan.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "is_farmer", "operator": "eq", "value": "true", "description": "Applicant must be an individual or joint cultivator/farmer"},
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant age must be at least 18 years"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card & PAN Card", "is_mandatory": True},
                {"document_name": "Land Record Documents (Patta/Chitta)", "is_mandatory": True},
                {"document_name": "Cropping pattern declaration", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Download one-page KCC Application Form from pmkisan.gov.in or bank website."},
                {"step_number": 2, "instruction": "Fill land details, crop cultivated, and attach land revenue records."},
                {"step_number": 3, "instruction": "Submit to your rural/commercial bank where you hold PM-KISAN account."},
                {"step_number": 4, "instruction": "Card issued within 14 working days with RuPay KCC card for ATM withdrawals."},
            ],
        },

        # 15. Pradhan Mantri Ujjwala Yojana (PMUY)
        {
            "title": "Pradhan Mantri Ujjwala Yojana (PMUY 2.0 - Free LPG)",
            "department": "Ministry of Petroleum and Natural Gas",
            "description": "Clean cooking fuel initiative providing deposit-free LPG gas connections to adult women belonging to poor and economically disadvantaged households.",
            "benefits": "Free LPG gas connection, first cylinder refill and gas stove completely free of cost, plus Rs. 300 targeted subsidy per 14.2 kg cylinder for up to 12 refills per year.",
            "category": "Women Welfare",
            "target_group": "BPL & Low Income Women",
            "state": "All India",
            "official_link": "https://www.pmuy.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "gender", "operator": "eq", "value": "female", "description": "Connection issued only in the name of an adult female family member"},
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Woman must be at least 18 years old"},
                {"field_name": "income", "operator": "lte", "value": "200000", "description": "Must belong to BPL/EWS or SECC household without existing LPG connection"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card of the applicant and adult family members", "is_mandatory": True},
                {"document_name": "Ration Card / BPL Certificate", "is_mandatory": True},
                {"document_name": "Bank Account Passbook (Aadhaar linked)", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Apply online at pmuy.gov.in or visit local Indane, Bharat Gas, or HP Gas distributor."},
                {"step_number": 2, "instruction": "Fill KYC declaration form confirming no existing LPG connection in the household."},
                {"step_number": 3, "instruction": "Distributor verifies address and biometric e-KYC."},
                {"step_number": 4, "instruction": "Collect free gas stove, regulator, and filled LPG cylinder."},
            ],
        },

        # 16. Atal Pension Yojana (APY)
        {
            "title": "Atal Pension Yojana (APY - Guaranteed Pension)",
            "department": "PFRDA & Ministry of Finance",
            "description": "Government-backed guaranteed monthly pension scheme aimed at unorganized sector workers, self-employed citizens, and daily wage earners.",
            "benefits": "Guaranteed lifetime monthly pension of Rs. 1,000, Rs. 2,000, Rs. 3,000, Rs. 4,000, or Rs. 5,000 from age 60 onwards, with spouse pension continuity and 100% corpus returned to nominees.",
            "category": "Senior Citizens",
            "target_group": "Unorganized Workers & General Citizens",
            "state": "All India",
            "official_link": "https://www.npscra.nsdl.co.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Entry age between 18 and 40 years"},
                {"field_name": "age", "operator": "lte", "value": "40", "description": "Maximum joining age is 40 years"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card", "is_mandatory": True},
                {"document_name": "Active Savings Bank Account with auto-debit facility", "is_mandatory": True},
                {"document_name": "Mobile Number", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit the bank branch where you have an active savings account or net banking portal."},
                {"step_number": 2, "instruction": "Choose your desired monthly pension amount (Rs. 1,000 - Rs. 5,000)."},
                {"step_number": 3, "instruction": "Authorize monthly auto-debit contribution (starts from as low as Rs. 42/month at age 18)."},
                {"step_number": 4, "instruction": "Receive APY PRAN number and digital subscriber card."},
            ],
        },

        # 17. Post-Matric Scholarship for SC/ST/OBC
        {
            "title": "Post-Matric Scholarship Scheme for SC/ST/OBC Students",
            "department": "Ministry of Social Justice & Empowerment",
            "description": "Centrally sponsored flagship scholarship to support higher education expenses for students belonging to Scheduled Castes, Scheduled Tribes, and Other Backward Classes.",
            "benefits": "Full compulsory non-refundable tuition fees reimbursed plus monthly maintenance allowance of up to Rs. 13,500 per annum based on study stream.",
            "category": "Education",
            "target_group": "SC/ST/OBC Students",
            "state": "All India",
            "official_link": "https://scholarships.gov.in",
            "is_active": True,
            "rules": [
                {"field_name": "is_student", "operator": "eq", "value": "true", "description": "Applicant must be an enrolled post-matric (Class 11 to PhD) student"},
                {"field_name": "category", "operator": "in", "value": "SC,ST,OBC", "description": "Must belong to SC, ST, or OBC category"},
                {"field_name": "income", "operator": "lte", "value": "250000", "description": "Annual family income must not exceed Rs. 2,50,000"},
            ],
            "documents": [
                {"document_name": "Community / Caste Certificate issued by competent authority", "is_mandatory": True},
                {"document_name": "Income Certificate (Current financial year)", "is_mandatory": True},
                {"document_name": "Previous Year Marksheet", "is_mandatory": True},
                {"document_name": "College Fee Receipt & Bonafide Certificate", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Register on the National Scholarship Portal (NSP) or State Scholarship Portal."},
                {"step_number": 2, "instruction": "Upload caste, income, and previous academic scorecards."},
                {"step_number": 3, "instruction": "Institute nodal officer verifies the bonafide enrollment."},
                {"step_number": 4, "instruction": "Scholarship sanctioned and credited directly into bank account via DBT."},
            ],
        },

        # 18. Stand-Up India Scheme
        {
            "title": "Stand-Up India Scheme (Loans for Women & SC/ST)",
            "department": "Ministry of Finance & SIDBI",
            "description": "Bank loans for setting up greenfield enterprises in manufacturing, services, agri-allied, or trading sectors by Scheduled Caste (SC), Scheduled Tribe (ST), and Women entrepreneurs.",
            "benefits": "Bank loans between Rs. 10 Lakh and Rs. 1 Crore covering up to 85% of total project cost with supportive handholding, training, and credit guarantee support.",
            "category": "Employment & Business",
            "target_group": "Women & SC/ST Entrepreneurs",
            "state": "All India",
            "official_link": "https://www.standupmitra.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be at least 18 years old"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card, PAN Card & Caste Certificate (if SC/ST)", "is_mandatory": True},
                {"document_name": "Detailed Project Report (DPR) with financial projections", "is_mandatory": True},
                {"document_name": "Company/Partnership registration document (if applicable)", "is_mandatory": False},
                {"document_name": "Pollution control NOC / Land lease agreement", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Visit standupmitra.in and register as a Trainee or Ready Borrower."},
                {"step_number": 2, "instruction": "Prepare Project Report with guidance from SIDBI or local MSME DI centre."},
                {"step_number": 3, "instruction": "Apply to scheduled commercial bank branch chosen on the portal."},
                {"step_number": 4, "instruction": "Sanction and disbursement of greenfield business loan."},
            ],
        },

        # 19. Prime Minister's Employment Generation Programme (PMEGP)
        {
            "title": "Prime Minister Employment Generation Programme (PMEGP)",
            "department": "Ministry of MSME & KVIC",
            "description": "Credit-linked subsidy programme to generate self-employment opportunities through establishment of micro-enterprises in non-farm sector.",
            "benefits": "Government margin money subsidy of 25% (Urban) to 35% (Rural/Special Category) on project costs up to Rs. 50 Lakh for manufacturing and Rs. 20 Lakh for services.",
            "category": "Employment & Business",
            "target_group": "Aspiring Entrepreneurs & Unemployed Youth",
            "state": "All India",
            "official_link": "https://www.kviconline.gov.in/pmegpeportal",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "18", "description": "Applicant must be aged 18 years or above"},
                {"field_name": "education", "operator": "in", "value": "8th pass,10th pass,12th pass,graduate,post-graduate,diploma", "description": "Minimum 8th pass for projects above Rs. 10 Lakh (mfg) / Rs. 5 Lakh (service)"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card & PAN Card", "is_mandatory": True},
                {"document_name": "Detailed Project Profile / DPR", "is_mandatory": True},
                {"document_name": "Special category certificate (SC/ST/OBC/Women/Ex-Servicemen if applicable)", "is_mandatory": False},
                {"document_name": "EDP Training Certificate (online EDP available post-approval)", "is_mandatory": False},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Apply online at kviconline.gov.in/pmegpeportal/."},
                {"step_number": 2, "instruction": "Select implementing agency (KVIC, KVIB, or District Industries Centre - DIC)."},
                {"step_number": 3, "instruction": "District Level Task Force Committee (DLTFC) reviews and forwards to chosen bank."},
                {"step_number": 4, "instruction": "Bank sanctions loan and subsidy is deposited into a 3-year locked Term Deposit (TDR)."},
            ],
        },

        # 20. Rashtriya Vayoshri Yojana (RVY)
        {
            "title": "Rashtriya Vayoshri Yojana (Assistive Devices for Seniors)",
            "department": "Ministry of Social Justice and Empowerment & ALIMCO",
            "description": "Provides physical aids and assisted-living devices for senior citizens belonging to BPL category suffering from age-related disabilities or infirmities.",
            "benefits": "100% free distribution of assisted-living devices including hearing aids, walking sticks with sensor, wheelchairs, spectacles, dentures, and tripod/quadpod crutches.",
            "category": "Senior Citizens",
            "target_group": "Senior Citizens with Infirmities",
            "state": "All India",
            "official_link": "https://alimco.in",
            "is_active": True,
            "rules": [
                {"field_name": "age", "operator": "gte", "value": "60", "description": "Applicant must be aged 60 years or above"},
                {"field_name": "income", "operator": "lte", "value": "180000", "description": "Low income / BPL category certificate"},
            ],
            "documents": [
                {"document_name": "Aadhaar Card / Age proof", "is_mandatory": True},
                {"document_name": "BPL Card / Income Certificate from Tehsildar", "is_mandatory": True},
                {"document_name": "Medical Officer certificate of age-related infirmity", "is_mandatory": True},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Register during District Assessment Camps organized by ALIMCO / District Administration."},
                {"step_number": 2, "instruction": "Medical assessment of disability/infirmity by government doctors."},
                {"step_number": 3, "instruction": "Device fitting and customization."},
                {"step_number": 4, "instruction": "Free distribution of durable assistive aids in public camp."},
            ],
        },
    ]

    for item in sample_schemes:
        scheme = Scheme(
            title=item["title"],
            department=item["department"],
            description=item["description"],
            benefits=item["benefits"],
            category=item["category"],
            target_group=item["target_group"],
            state=item["state"],
            official_link=item["official_link"],
            is_active=item["is_active"],
        )
        db.add(scheme)
        db.flush()

        for rule in item["rules"]:
            db.add(EligibilityRule(scheme_id=scheme.id, **rule))

        for document in item["documents"]:
            db.add(SchemeDocument(scheme_id=scheme.id, **document))

        for step in item["steps"]:
            db.add(ApplicationStep(scheme_id=scheme.id, **step))

    db.commit()
    print(f"Successfully seeded {len(sample_schemes)} comprehensive government welfare schemes.")
    db.close()


if __name__ == "__main__":
    seed_schemes()
