USE smartgov_ai;

-- 1. PM Scholarship for students
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('PM Scholarship Scheme', 'Ministry of Education',
  'Financial assistance for meritorious students from low-income families to pursue higher education.',
  'Up to Rs. 50,000 per year for tuition and living expenses.',
  'Education', 'Students', 'All India', 'https://scholarships.gov.in', TRUE);
SET @s1 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s1, 'is_student', 'eq', 'true', 'Applicant must be a currently enrolled student'),
 (@s1, 'income', 'lte', '250000', 'Family annual income must be Rs. 2,50,000 or below'),
 (@s1, 'age', 'lte', '25', 'Applicant age must be 25 or below');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s1, 'Aadhaar Card', TRUE), (@s1, 'Income Certificate', TRUE), (@s1, 'Marksheet of last exam', TRUE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s1, 1, 'Register on the National Scholarship Portal'),
 (@s1, 2, 'Fill the application form with academic and income details'),
 (@s1, 3, 'Upload required documents and submit before the deadline');

-- 2. PM Kisan Samman Nidhi for farmers
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('PM-KISAN Samman Nidhi', 'Ministry of Agriculture',
  'Income support scheme for small and marginal farmer families.',
  'Rs. 6,000 per year in three equal installments directly to bank account.',
  'Agriculture', 'Farmers', 'All India', 'https://pmkisan.gov.in', TRUE);
SET @s2 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s2, 'is_farmer', 'eq', 'true', 'Applicant must be a farmer'),
 (@s2, 'income', 'lte', '200000', 'Land-owning farmer families with modest income');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s2, 'Aadhaar Card', TRUE), (@s2, 'Land Ownership Papers', TRUE), (@s2, 'Bank Passbook', TRUE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s2, 1, 'Visit the PM-KISAN portal or nearest Common Service Centre'),
 (@s2, 2, 'Submit land records and bank details'),
 (@s2, 3, 'Track application status online');

-- 3. Mahila Samman Savings scheme for women
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('Mahila Samman Savings Certificate', 'Ministry of Finance',
  'Small savings scheme exclusively for women and girls to encourage financial independence.',
  'Fixed 7.5% interest rate on deposits up to Rs. 2 lakh for 2 years.',
  'Women Welfare', 'Women', 'All India', 'https://financialservices.gov.in', TRUE);
SET @s3 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s3, 'gender', 'eq', 'female', 'Open only to women and girl children');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s3, 'Aadhaar Card', TRUE), (@s3, 'PAN Card', FALSE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s3, 1, 'Visit nearest Post Office or authorised bank'),
 (@s3, 2, 'Fill account opening form and deposit amount'),
 (@s3, 3, 'Collect certificate of deposit');

-- 4. National Career Service for job seekers
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('National Career Service (NCS) Registration', 'Ministry of Labour and Employment',
  'Online platform connecting job seekers with employers, training and career counselling.',
  'Free job matching, skill training referrals, and career counselling.',
  'Employment', 'Job Seekers', 'All India', 'https://ncs.gov.in', TRUE);
SET @s4 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s4, 'age', 'gte', '18', 'Applicant must be at least 18 years old'),
 (@s4, 'occupation', 'eq', 'unemployed', 'Open to job seekers currently unemployed');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s4, 'Aadhaar Card', TRUE), (@s4, 'Educational Certificates', TRUE), (@s4, 'Resume', FALSE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s4, 1, 'Register on the NCS portal with basic details'),
 (@s4, 2, 'Complete your profile and upload resume'),
 (@s4, 3, 'Browse and apply to matched job listings');

-- 5. Indira Gandhi National Old Age Pension
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('Indira Gandhi National Old Age Pension Scheme', 'Ministry of Rural Development',
  'Monthly pension support for senior citizens living below the poverty line.',
  'Rs. 200-500 monthly pension depending on state top-up.',
  'Senior Citizens', 'Senior Citizens', 'All India', 'https://nsap.nic.in', TRUE);
SET @s5 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s5, 'age', 'gte', '60', 'Applicant must be 60 years or older'),
 (@s5, 'income', 'lte', '150000', 'Applicant must belong to a low-income household');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s5, 'Aadhaar Card', TRUE), (@s5, 'Age Proof', TRUE), (@s5, 'BPL Certificate', TRUE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s5, 1, 'Apply at the local Gram Panchayat or Municipal office'),
 (@s5, 2, 'Submit age and income proof'),
 (@s5, 3, 'Receive pension via bank account or money order');

-- 6. Disability Pension Scheme
INSERT INTO schemes (title, department, description, benefits, category, target_group, state, official_link, is_active)
VALUES ('National Disability Pension Scheme', 'Ministry of Social Justice and Empowerment',
  'Monthly financial assistance for persons with severe or multiple disabilities.',
  'Rs. 300-500 monthly pension plus access to assistive devices.',
  'Disability Support', 'Persons with Disability', 'All India', 'https://disabilityaffairs.gov.in', TRUE);
SET @s6 = LAST_INSERT_ID();
INSERT INTO eligibility_rules (scheme_id, field_name, operator, value, description) VALUES
 (@s6, 'has_disability', 'eq', 'true', 'Applicant must have a certified disability'),
 (@s6, 'income', 'lte', '150000', 'Applicant must belong to a low-income household');
INSERT INTO scheme_documents (scheme_id, document_name, is_mandatory) VALUES
 (@s6, 'Aadhaar Card', TRUE), (@s6, 'Disability Certificate', TRUE), (@s6, 'Income Certificate', TRUE);
INSERT INTO application_steps (scheme_id, step_number, instruction) VALUES
 (@s6, 1, 'Obtain a disability certificate from a government hospital'),
 (@s6, 2, 'Apply at the district Social Welfare office'),
 (@s6, 3, 'Track pension disbursement status online');
