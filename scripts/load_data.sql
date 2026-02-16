
	INSERT INTO Staging.contract_type(contract_name)
	SELECT DISTINCT contract FROM dbo.TelcoClean r
	WHERE NOT EXISTS (
	SELECT 1
	FROM Staging.contract_type s
	WHERE s.contract_name = r.Contract

	);

	
	

	INSERT INTO staging.payment_method (payment_method, is_electronic)
	SELECT DISTINCT
		PaymentMethod,
		CASE 
			WHEN PaymentMethod LIKE '%automatic%' THEN 1
			ELSE 0
		END
	FROM dbo.TelcoClean r
	WHERE NOT EXISTS (
		SELECT 1
		FROM staging.payment_method s
		WHERE s.payment_method = r.PaymentMethod
	);
	


	INSERT INTO staging.customer (
		customer_id,
		gender,
		senior_citizen,
		partner,
		dependents,
		tenure_months
	)
	SELECT
		customerID,
		CASE 
			WHEN gender = 'Male' THEN 'M'
			WHEN gender = 'Female' THEN 'F'
			ELSE NULL
		END,
		TRY_CAST(SeniorCitizen AS INT),
		CASE WHEN partner = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN dependents = 'Yes' THEN 1 ELSE 0 END,
		TRY_CAST(tenure AS INT)
	FROM dbo.TelcoClean r
	WHERE NOT EXISTS (
		SELECT 1
		FROM staging.customer s
		WHERE s.customer_id = r.customerID
	);
	

	INSERT INTO staging.service_profile (
		customer_key,
		phone_service,
		multiple_lines,
		internet_service,
		online_security,
		online_backup,
		device_protection,
		tech_support,
		streaming_tv,
		streaming_movies
	)
	SELECT
		c.customer_key,
		CASE WHEN r.PhoneService = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.MultipleLines = 'Yes' THEN 1 ELSE 0 END,
		r.InternetService,
		CASE WHEN r.OnlineSecurity = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.OnlineBackup = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.DeviceProtection = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.TechSupport = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.StreamingTV = 'Yes' THEN 1 ELSE 0 END,
		CASE WHEN r.StreamingMovies = 'Yes' THEN 1 ELSE 0 END
	FROM dbo.TelcoClean r
	JOIN staging.customer c 
		ON c.customer_id = r.customerID
	WHERE NOT EXISTS (
		SELECT 1
		FROM staging.service_profile sp
		WHERE sp.customer_key = c.customer_key
	);
	

	INSERT INTO staging.customer_contract (
		customer_key,
		contract_key,
		payment_key,
		paperless_billing,
		monthly_charges,
		total_charges,
		churn
	)
	SELECT
		c.customer_key,
		ct.contract_key,
		pm.payment_key,
		CASE WHEN r.PaperlessBilling = 'Yes' THEN 1 ELSE 0 END,
		TRY_CAST(r.MonthlyCharges AS DECIMAL(10,2)),
		TRY_CAST(r.TotalCharges AS DECIMAL(10,2)),
		CASE WHEN r.churn = 'Yes' THEN 1 ELSE 0 END
	FROM dbo.TelcoClean r
	JOIN staging.customer c
		ON c.customer_id = r.customerID
	JOIN staging.contract_type ct
		ON ct.contract_name = r.contract
	JOIN staging.payment_method pm
		ON pm.payment_method = r.PaymentMethod
	WHERE NOT EXISTS (
		SELECT 1
		FROM staging.customer_contract cc
		WHERE cc.customer_key = c.customer_key
	)
