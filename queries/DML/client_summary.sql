SELECT 
    -- Client metadata
    C.CLIENT_ID,
    C.CLIENT_NAME,
    C.SECTOR,
    C.CONTRACT_TIER,
    C.SIGN_UP_DATE,
    
    -- Basic event metrics
    COUNT(E.EVENT_ID) as TOTAL_EVENTS,
    SUM(E.AMOUNT) as TOTAL_VOLUME,
    AVG(E.AMOUNT) as AVG_TRANSACTION_AMOUNT,
    
    -- Status counts
    SUM(CASE WHEN E.STATUS = 'completed' THEN 1 ELSE 0 END) as COMPLETED_EVENTS,
    SUM(CASE WHEN E.STATUS = 'failed' THEN 1 ELSE 0 END) as FAILED_EVENTS,
    SUM(CASE WHEN E.STATUS = 'processing' THEN 1 ELSE 0 END) as PROCESSING_EVENTS,
    
    -- Retry metrics
    COUNT(R.RETRY_ID) as TOTAL_RETRIES,
    SUM(CASE WHEN R.RETRY_STATUS = 'success' THEN 1 ELSE 0 END) as SUCCESSFUL_RETRIES,
    
    -- Pay-in ratio
    ROUND(
        SUM(
            CASE WHEN E.TYPE = 'pay_in' THEN 1 ELSE 0 END
        ) * 100.0 / 
        NULLIF(COUNT(E.EVENT_ID), 0), 
        2
    ) as PAY_IN_RATIO,
    
    -- Pay-out ratio
    ROUND(
        SUM(
            CASE WHEN E.TYPE = 'pay_out' THEN 1 ELSE 0 END
        ) * 100.0 / 
        NULLIF(COUNT(E.EVENT_ID), 0), 
        2
    ) as PAY_OUT_RATIO,

    -- Fail rate
    ROUND(
        SUM(
            CASE WHEN E.STATUS = 'failed' THEN 1 ELSE 0 END
        ) * 100.0 / 
        NULLIF(COUNT(E.EVENT_ID), 0), 
        2
    ) as FAIL_RATE,
    
    -- AVG Delay
    ROUND(
        AVG(
            CASE 
                WHEN E.COMPLETED_AT IS NOT NULL AND E.CREATED_AT IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (CAST(E.COMPLETED_AT AS TIMESTAMP) - CAST(E.CREATED_AT AS TIMESTAMP))) / 3600.0
                ELSE NULL 
            END
        ), 
        2
    ) AS AVG_DELAY_HOURS,
    
    -- Retry rate (% of events that had retries)
    ROUND(
        COUNT(DISTINCT R.ORIGINAL_EVENT_ID) * 100.0 / 
        NULLIF(COUNT(E.EVENT_ID), 0), 
        2
    ) AS RETRY_RATE

FROM CLIENTS AS C
LEFT JOIN EVENTS AS E
  ON C.CLIENT_ID = E.CLIENT_ID
LEFT JOIN RETRY_LOGS AS R
  ON E.EVENT_ID = R.ORIGINAL_EVENT_ID
GROUP BY
  C.CLIENT_ID
  , C.CLIENT_NAME
  , C.SECTOR
  , C.CONTRACT_TIER
  , C.SIGN_UP_DATE
ORDER BY TOTAL_VOLUME DESC NULLS LAST