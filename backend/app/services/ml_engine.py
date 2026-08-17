from typing import Dict, Any, List

class MLEngineService:
    """
    ML Intelligence Engine for Lead Scoring, Churn Prediction, Customer Health, and Upsell Intelligence.
    Uses multi-factor scoring logic with explainability feature attribution.
    """

    @staticmethod
    def calculate_lead_score(
        company_size: str,
        industry: str,
        source: str,
        deal_value: float,
        activity_count: int = 1
    ) -> Dict[str, Any]:
        score = 50  # Baseline
        factors = []

        # Company Size impact
        size_str = str(company_size).lower()
        if "1000+" in size_str or "enterprise" in size_str:
            score += 25
            factors.append("Enterprise scale company (1000+ employees)")
        elif "201-1000" in size_str or "51-200" in size_str:
            score += 15
            factors.append("Mid-market target company size")
        elif "11-50" in size_str:
            score += 5
            factors.append("Small business segment")

        # Industry impact
        ind_str = str(industry).lower()
        if any(i in ind_str for i in ["tech", "software", "finance", "fintech", "healthcare"]):
            score += 15
            factors.append(f"High-fit target industry ({industry})")
        else:
            score += 5

        # Deal value impact
        if deal_value >= 50000:
            score += 15
            factors.append(f"High prospective deal value (${deal_value:,.0f})")
        elif deal_value >= 15000:
            score += 10
            factors.append(f"Solid deal value (${deal_value:,.0f})")

        # Source impact
        src_str = str(source).lower()
        if any(s in src_str for s in ["demo", "inbound", "referral"]):
            score += 10
            factors.append(f"High intent lead source ({source})")
        elif "outbound" in src_str:
            score += 5

        # Activity impact
        if activity_count >= 3:
            score += 10
            factors.append(f"High engagement level ({activity_count}+ touchpoints)")

        # Cap score between 0 and 100
        final_score = max(5, min(98, score))
        conversion_prob = round(final_score / 100.0, 2)
        
        if final_score >= 75:
            risk_level = "Low"
            action = f"High priority account ({final_score}/100). Schedule a discovery call within 2 hours."
        elif final_score >= 50:
            risk_level = "Medium"
            action = f"Qualified prospect ({final_score}/100). Send customized industry demo & case study."
        else:
            risk_level = "High"
            action = f"Nurture status ({final_score}/100). Add to 14-day automated email campaign."

        return {
            "score": final_score,
            "conversion_prob": conversion_prob,
            "risk_level": risk_level,
            "factors": factors,
            "recommended_action": action
        }

    @staticmethod
    def calculate_customer_health(
        mrr: float,
        ticket_count: int,
        negative_sentiment_count: int,
        days_since_last_activity: int
    ) -> Dict[str, Any]:
        health = 85  # Baseline

        factors = []
        if days_since_last_activity > 30:
            health -= 25
            factors.append("Low recent product engagement (>30 days inactive)")
        elif days_since_last_activity > 14:
            health -= 10
            factors.append("Decreasing activity frequency")

        if ticket_count > 5:
            health -= 20
            factors.append(f"High support volume ({ticket_count} recent tickets)")
        
        if negative_sentiment_count > 0:
            health -= 25
            factors.append(f"Negative sentiment logged in support conversations ({negative_sentiment_count} events)")

        if mrr >= 5000:
            health += 10
            factors.append("High MRR enterprise account commitment")

        health = max(10, min(100, health))
        
        if health >= 75:
            status = "Healthy"
            churn_risk_score = round((100 - health) / 100.0, 2)
            churn_level = "Low"
        elif health >= 50:
            status = "At Risk"
            churn_risk_score = round((100 - health) / 100.0, 2)
            churn_level = "Medium"
        else:
            status = "Critical"
            churn_risk_score = round((100 - health) / 100.0, 2)
            churn_level = "High"

        return {
            "health_score": health,
            "health_status": status,
            "churn_risk_score": churn_risk_score,
            "churn_risk_level": churn_level,
            "risk_factors": factors
        }

    @staticmethod
    def calculate_upsell_opportunity(
        mrr: float,
        health_score: int,
        plan_tier: str
    ) -> Dict[str, Any]:
        if health_score >= 80 and plan_tier != "Enterprise":
            target_plan = "Enterprise" if plan_tier == "Business" else "Business"
            estimated_expansion_mrr = mrr * 0.5
            return {
                "has_opportunity": True,
                "opportunity_type": "Tier Upgrade",
                "recommended_plan": target_plan,
                "estimated_expansion_mrr": estimated_expansion_mrr,
                "reasoning": f"Customer health is outstanding ({health_score}/100). High probability for upgrade from {plan_tier} to {target_plan}."
            }
        elif health_score >= 70:
            return {
                "has_opportunity": True,
                "opportunity_type": "Additional Seats / API Quota",
                "recommended_plan": plan_tier,
                "estimated_expansion_mrr": mrr * 0.2,
                "reasoning": "High product utilization suggests account is ready for 20% seat expansion."
            }
        else:
            return {
                "has_opportunity": False,
                "opportunity_type": "None",
                "recommended_plan": plan_tier,
                "estimated_expansion_mrr": 0.0,
                "reasoning": "Focus on customer success and health recovery before proposing expansion."
            }

ml_engine = MLEngineService()
