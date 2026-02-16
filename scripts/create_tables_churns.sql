IF OBJECT_ID('dbo.telco_raw', 'U') IS NOT NULL
    DROP TABLE dbo.telco_raw;

CREATE TABLE dbo.telco_raw (
    customer_id         VARCHAR(20) NOT NULL,
    gender              VARCHAR(20),
    senior_citizen      VARCHAR(5),
    partner             VARCHAR(5),
    dependents          VARCHAR(5),
    tenure              VARCHAR(10),
    phone_service       VARCHAR(5),
    multiple_lines      VARCHAR(50),
    internet_service    VARCHAR(50),
    online_security     VARCHAR(50),
    online_backup       VARCHAR(50),
    device_protection   VARCHAR(50),
    tech_support        VARCHAR(50),
    streaming_tv        VARCHAR(50),
    streaming_movies    VARCHAR(50),
    contract            VARCHAR(50),
    paperless_billing   VARCHAR(5),
    payment_method      VARCHAR(100),
    monthly_charges     VARCHAR(20),
    total_charges       VARCHAR(20),
    churn               VARCHAR(5),
    load_dttm           DATETIME2 DEFAULT SYSDATETIME(),
    source_file         VARCHAR(255),
    row_id              INT IDENTITY(1,1)
);
GO

IF OBJECT_ID('staging.contract_type', 'U') IS NOT NULL
    DROP TABLE staging.contract_type;
CREATE TABLE staging.contract_type (
    contract_key INT IDENTITY PRIMARY KEY,
    contract_name VARCHAR(50) UNIQUE NOT NULL
);

GO

IF OBJECT_ID('staging.payment_method', 'U') IS NOT NULL
    DROP TABLE staging.payment_method;
CREATE TABLE staging.payment_method (
    payment_key INT IDENTITY PRIMARY KEY,
    payment_method VARCHAR(100) UNIQUE NOT NULL,
    is_electronic BIT
);
GO

IF OBJECT_ID('staging.customer', 'U') IS NOT NULL
    DROP TABLE staging.customer;

CREATE TABLE staging.customer (
    customer_key     INT IDENTITY PRIMARY KEY,
    customer_id      VARCHAR(20) UNIQUE NOT NULL,
    gender           CHAR(1),
    senior_citizen   BIT,
    partner          BIT,
    dependents       BIT,
    tenure_months    INT,
    record_dttm      DATETIME2 DEFAULT SYSDATETIME()
);
GO

IF OBJECT_ID('staging.service_profile', 'U') IS NOT NULL
    DROP TABLE staging.service_profile;

CREATE TABLE staging.service_profile (
    customer_key       INT PRIMARY KEY,
    phone_service      BIT,
    multiple_lines     BIT,
    internet_service   VARCHAR(50),
    online_security    BIT,
    online_backup      BIT,
    device_protection  BIT,
    tech_support       BIT,
    streaming_tv       BIT,
    streaming_movies   BIT,
    CONSTRAINT fk_sp_customer
        FOREIGN KEY (customer_key)
        REFERENCES staging.customer(customer_key)
);
GO

IF OBJECT_ID('staging.customer_contract', 'U') IS NOT NULL
    DROP TABLE staging.customer_contract;

CREATE TABLE staging.customer_contract (
    customer_key      INT PRIMARY KEY,
    contract_key      INT NOT NULL,
    payment_key       INT NOT NULL,
    paperless_billing BIT,
    monthly_charges   DECIMAL(10,2),
    total_charges     DECIMAL(10,2),
    churn             BIT,
    contract_dttm     DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT fk_cc_customer
        FOREIGN KEY (customer_key)
        REFERENCES staging.customer(customer_key),
    CONSTRAINT fk_cc_contract
        FOREIGN KEY (contract_key)
        REFERENCES staging.contract_type(contract_key),
    CONSTRAINT fk_cc_payment
        FOREIGN KEY (payment_key)
        REFERENCES staging.payment_method(payment_key)
);
GO

IF OBJECT_ID('oper.dim_customer', 'U') IS NOT NULL
    DROP TABLE oper.dim_customer;
CREATE TABLE oper.dim_customer (
    customer_key   INT PRIMARY KEY,
    customer_id    VARCHAR(20),
    gender         CHAR(1),
    senior_citizen BIT,
    partner        BIT,
    dependents     BIT,
    tenure_months  INT,
    tenure_group   VARCHAR(10)
);
GO

IF OBJECT_ID('oper.dim_contract', 'U') IS NOT NULL
    DROP TABLE oper.dim_contract;
CREATE TABLE oper.dim_contract (
    contract_key  INT PRIMARY KEY,
    contract_name VARCHAR(50)
);
GO


IF OBJECT_ID('oper.dim_payment', 'U') IS NOT NULL
    DROP TABLE oper.dim_payment;

CREATE TABLE oper.dim_payment (
    payment_key     INT PRIMARY KEY,
    payment_method  VARCHAR(100),
    is_electronic   BIT
);
GO

IF OBJECT_ID('oper.dim_service', 'U') IS NOT NULL
    DROP TABLE oper.dim_service;

CREATE TABLE oper.dim_service (
    customer_key       INT PRIMARY KEY,
    phone_service      BIT,
    multiple_lines     BIT,
    internet_service   VARCHAR(50),
    online_security    BIT,
    online_backup      BIT,
    device_protection  BIT,
    tech_support       BIT,
    streaming_tv       BIT,
    streaming_movies   BIT
);
GO

IF OBJECT_ID('oper.fact_customer_churn', 'U') IS NOT NULL
    DROP TABLE oper.fact_customer_churn;
CREATE TABLE oper.fact_customer_churn (
    customer_key     INT PRIMARY KEY,
    contract_key     INT,
    payment_key      INT,
    monthly_charges  DECIMAL(10,2),
    total_charges    DECIMAL(10,2),
    churn            BIT,
    snapshot_dttm    DATETIME2 DEFAULT SYSDATETIME(),
    CONSTRAINT fk_fc_customer
        FOREIGN KEY (customer_key)
        REFERENCES oper.dim_customer(customer_key),
    CONSTRAINT fk_fc_contract
        FOREIGN KEY (contract_key)
        REFERENCES oper.dim_contract(contract_key),
    CONSTRAINT fk_fc_payment
        FOREIGN KEY (payment_key)
        REFERENCES oper.dim_payment(payment_key)
);
GO
