# src/etl/create_views.py
from sqlalchemy import text
from config import engine
import logging

logger = logging.getLogger(__name__)

def create_analytics_views():
    """Create materialized views for dashboard analytics."""
    logger.info("\n" + "="*60)
    logger.info("CREATING ANALYTICS VIEWS")
    logger.info("="*60)
    
    views = {
        "mv_revenue_cycle_kpis": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_cycle_kpis AS
            SELECT 
                DATE_TRUNC('month', c.filing_date) AS claim_month,
                COUNT(DISTINCT c.claim_id) AS total_claims,
                COUNT(DISTINCT CASE WHEN c.claim_status = 'Denied' THEN c.claim_id END) AS denied_claims,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.claim_status = 'Denied' THEN c.claim_id END) / 
                      NULLIF(COUNT(DISTINCT c.claim_id), 0), 2) AS denial_rate_pct,
                SUM(c.total_charge) AS total_charges,
                SUM(COALESCE(cli.payment_amount, 0)) AS total_collected,
                ROUND(100.0 * SUM(COALESCE(cli.payment_amount, 0)) / 
                      NULLIF(SUM(c.total_charge), 0), 2) AS net_collection_rate_pct,
                SUM(COALESCE(cli.adjustment_amount, 0)) AS total_adjustments
            FROM claims c
            LEFT JOIN claim_line_items cli ON c.claim_id = cli.claim_id
            GROUP BY DATE_TRUNC('month', c.filing_date)
            ORDER BY claim_month
        """,
        
        "mv_provider_productivity": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_provider_productivity AS
            SELECT 
                p.provider_id,
                p.first_name || ' ' || p.last_name AS provider_name,
                p.specialty,
                DATE_TRUNC('month', a.scheduled_time) AS visit_month,
                COUNT(DISTINCT a.appointment_id) AS total_appointments,
                COUNT(DISTINCT CASE WHEN a.status = 'Completed' THEN a.appointment_id END) AS completed_visits,
                COUNT(DISTINCT CASE WHEN a.status = 'No-Show' THEN a.appointment_id END) AS no_shows,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.status = 'No-Show' THEN a.appointment_id END) / 
                      NULLIF(COUNT(DISTINCT a.appointment_id), 0), 2) AS no_show_rate_pct,
                ROUND(AVG(CASE WHEN a.actual_start_time IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (a.actual_start_time - a.scheduled_time))/60 
                END), 0) AS avg_wait_minutes,
                COUNT(DISTINCT e.encounter_id) AS encounters,
                SUM(COALESCE(pr.charge_amount, 0)) AS total_charges
            FROM providers p
            LEFT JOIN appointments a ON p.provider_id = a.provider_id
            LEFT JOIN encounters e ON a.appointment_id = e.appointment_id
            LEFT JOIN procedures pr ON e.encounter_id = pr.encounter_id
            GROUP BY p.provider_id, provider_name, p.specialty, DATE_TRUNC('month', a.scheduled_time)
            ORDER BY visit_month, provider_name
        """,
        
        "mv_payer_analysis": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_payer_analysis AS
            SELECT 
                ic.company_name AS payer,
                ic.payer_id,
                DATE_TRUNC('month', c.filing_date) AS claim_month,
                COUNT(DISTINCT c.claim_id) AS total_claims,
                SUM(c.total_charge) AS total_charges,
                SUM(COALESCE(cli.payment_amount, 0)) AS total_paid,
                SUM(COALESCE(cli.adjustment_amount, 0)) AS total_adjustments,
                ROUND(100.0 * SUM(COALESCE(cli.payment_amount, 0)) / 
                      NULLIF(SUM(c.total_charge), 0), 2) AS collection_rate_pct,
                ROUND(AVG(c.filing_date - c.adjudication_date), 0) AS avg_days_to_pay
            FROM claims c
            JOIN encounters e ON c.encounter_id = e.encounter_id
            JOIN appointments a ON e.appointment_id = a.appointment_id
            JOIN patient_insurance pi ON a.patient_id = pi.patient_id
            JOIN insurance_companies ic ON pi.insurance_company_id = ic.insurance_company_id
            LEFT JOIN claim_line_items cli ON c.claim_id = cli.claim_id
            GROUP BY ic.company_name, ic.payer_id, DATE_TRUNC('month', c.filing_date)
            ORDER BY claim_month, payer
        """,
        
        "mv_procedure_utilization": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_procedure_utilization AS
            SELECT 
                pr.cpt_code,
                pr.description,
                COUNT(*) AS frequency,
                SUM(pr.units) AS total_units,
                SUM(pr.charge_amount) AS total_charges,
                AVG(pr.charge_amount) AS avg_charge,
                COUNT(DISTINCT pr.encounter_id) AS unique_encounters
            FROM procedures pr
            GROUP BY pr.cpt_code, pr.description
            ORDER BY frequency DESC
        """,
        
        "mv_diagnosis_trends": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_diagnosis_trends AS
            SELECT 
                d.icd_code,
                d.description,
                DATE_TRUNC('month', e.encounter_date) AS dx_month,
                COUNT(*) AS diagnosis_count,
                COUNT(DISTINCT e.encounter_id) AS unique_encounters,
                COUNT(DISTINCT a.patient_id) AS unique_patients
            FROM diagnoses d
            JOIN encounters e ON d.encounter_id = e.encounter_id
            JOIN appointments a ON e.appointment_id = a.appointment_id
            GROUP BY d.icd_code, d.description, DATE_TRUNC('month', e.encounter_date)
            ORDER BY dx_month, diagnosis_count DESC
        """,
        
        "mv_daily_revenue": """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_revenue AS
            SELECT 
                e.encounter_date,
                p.specialty,
                COUNT(DISTINCT e.encounter_id) AS total_encounters,
                SUM(pr.charge_amount) AS total_charges,
                SUM(COALESCE(cli.payment_amount, 0)) AS total_collected,
                SUM(COALESCE(cli.adjustment_amount, 0)) AS total_adjustments,
                ROUND(100.0 * SUM(COALESCE(cli.payment_amount, 0)) / 
                      NULLIF(SUM(pr.charge_amount), 0), 2) AS daily_collection_rate
            FROM encounters e
            JOIN appointments a ON e.appointment_id = a.appointment_id
            JOIN providers p ON a.provider_id = p.provider_id
            LEFT JOIN procedures pr ON e.encounter_id = pr.encounter_id
            LEFT JOIN claims c ON e.encounter_id = c.encounter_id
            LEFT JOIN claim_line_items cli ON c.claim_id = cli.claim_id
            GROUP BY e.encounter_date, p.specialty
            ORDER BY e.encounter_date DESC
        """
    }
    
    with engine.connect() as conn:
        for view_name, view_sql in views.items():
            try:
                conn.execute(text(view_sql))
                logger.info(f"✓ Created {view_name}")
            except Exception as e:
                logger.error(f"✗ Error creating {view_name}: {e}")
        conn.commit()
    
    logger.info("✓ All analytics views created")

def refresh_views():
    """Refresh all materialized views."""
    logger.info("Refreshing materialized views...")
    
    views = [
        "mv_revenue_cycle_kpis",
        "mv_provider_productivity",
        "mv_payer_analysis",
        "mv_procedure_utilization",
        "mv_diagnosis_trends",
        "mv_daily_revenue"
    ]
    
    with engine.connect() as conn:
        for view in views:
            try:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                logger.info(f"✓ Refreshed {view}")
            except Exception as e:
                logger.warning(f"  Could not refresh {view}: {e}")
        conn.commit()

if __name__ == "__main__":
    create_analytics_views()