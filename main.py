from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import logging
import os
from dataclasses import dataclass

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mutual Fund Analysis API",
    version="1.0.0",
    description="AI-powered comprehensive mutual fund analysis platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Use environment variables in production
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "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")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai/chat/completions"

# Request/Response Models
class MutualFundRequest(BaseModel):
    mutual_fund_name: str
    
class AnalysisResponse(BaseModel):
    status: str
    fund_name: str
    analysis: Dict
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    version: str

@dataclass
class AnalysisResult:
    fund_analysis: str = ""
    sentiment_analysis: str = ""
    macro_analysis: str = ""
    final_report: str = ""

class MutualFundAnalyzer:
    def __init__(self):
        self.session = None
        self.request_count = 0
    
    async def get_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def call_perplexity_api(self, prompt: str, role: str = "assistant") -> str:
        """Make API call to Perplexity with error handling"""
        session = await self.get_session()
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        try:
            self.request_count += 1
            logger.info(f"Making Perplexity API call #{self.request_count}")
            
            async with session.post(PERPLEXITY_BASE_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    logger.error(f"Perplexity API error: {response.status} - {error_text}")
                    return f"Error calling Perplexity API: {response.status}. Please try again."
        except asyncio.TimeoutError:
            logger.error("Perplexity API timeout")
            return "Request timeout. Please try again with a shorter fund name."
        except Exception as e:
            logger.error(f"Exception calling Perplexity API: {str(e)}")
            return f"Service temporarily unavailable. Please try again later."
    
    async def analyze_mutual_fund(self, fund_name: str) -> str:
        """Mutual Fund Analysis Agent"""
        prompt = f"""
        As an expert Mutual Fund Analyst specializing in Indian mutual funds, provide a comprehensive analysis of {fund_name}.

        Please analyze:
        1. Fund Overview (AUM, expense ratio, fund manager, investment style)
        2. Historical Performance (1Y, 3Y, 5Y returns vs benchmark and category)
        3. Portfolio Analysis (top holdings, sector allocation, market cap distribution)
        4. Risk Metrics (beta, standard deviation, Sharpe ratio)
        5. Fund Manager track record
        6. Strengths and weaknesses
        7. Suitability for different investor profiles

        Provide specific data points and numbers wherever possible. Focus on recent data from the last 12 months.
        """
        
        return await self.call_perplexity_api(prompt)
    
    async def analyze_sentiment(self, fund_name: str) -> str:
        """Financial Sentiment Analysis Agent"""
        prompt = f"""
        As a Financial Sentiment Analysis expert, analyze the current market sentiment around {fund_name}.

        Research and analyze:
        1. Recent news articles and press releases (last 4 weeks)
        2. Expert commentary and analyst recommendations
        3. Social media sentiment from financial platforms
        4. Any significant events affecting the fund or its holdings
        5. Investor sentiment trends
        6. Media coverage tone (positive/neutral/negative)

        Provide:
        - Overall sentiment score and direction
        - Key positive and negative catalysts
        - Recent events impact
        - Forward-looking sentiment indicators

        Focus on credible financial news sources and expert opinions.
        """
        
        return await self.call_perplexity_api(prompt)
    
    async def analyze_macroeconomic(self, fund_name: str) -> str:
        """Macroeconomic Analysis Agent"""
        prompt = f"""
        As a Macroeconomic Analysis expert, analyze how current macroeconomic conditions impact {fund_name}.

        Analyze current economic indicators:
        1. India's GDP growth trends and forecasts
        2. RBI monetary policy and interest rate outlook
        3. Inflation trends (CPI, WPI) and impact
        4. Global economic factors affecting Indian markets
        5. Currency trends (INR/USD) and FII flows
        6. Government policies affecting mutual funds/capital markets
        7. Sectoral economic trends relevant to the fund's holdings

        Provide:
        - Current economic environment summary
        - Key macroeconomic risks and opportunities
        - Specific implications for the fund's performance
        - Forward-looking economic scenarios
        - Policy changes that could impact the fund

        Focus on recent data and RBI/government announcements.
        """
        
        return await self.call_perplexity_api(prompt)
    
    async def compile_final_report(self, fund_name: str, fund_analysis: str, sentiment_analysis: str, macro_analysis: str) -> str:
        """Research Report Compilation Agent"""
        prompt = f"""
        As an expert Research Report Writer, compile a comprehensive investment research report for {fund_name} using the following analyses:

        FUND ANALYSIS:
        {fund_analysis}

        SENTIMENT ANALYSIS:
        {sentiment_analysis}

        MACROECONOMIC ANALYSIS:
        {macro_analysis}

        Create a professional research report with the following structure:

        # Investment Research Report: {fund_name}

        ## Executive Summary
        - Key findings and investment recommendation
        - Target investor profile
        - Risk rating

        ## Fund Overview
        - Basic fund details and strategy

        ## Performance Analysis
        - Historical performance summary
        - Risk-adjusted returns

        ## Current Market Environment
        - Macroeconomic backdrop
        - Market sentiment

        ## Investment Thesis
        - Strengths and opportunities
        - Risks and challenges

        ## Final Recommendation
        - Investment rating (BUY/HOLD/SELL)
        - Rationale for recommendation
        - Suitable investor profile
        - Investment horizon

        Use professional investment research language and provide specific, actionable insights.
        """
        
        return await self.call_perplexity_api(prompt)

# Global analyzer instance
analyzer = MutualFundAnalyzer()

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Starting Mutual Fund Analysis API")
    logger.info(f"Perplexity API Key configured: {'Yes' if PERPLEXITY_API_KEY else 'No'}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    await analyzer.close_session()
    logger.info("Shutting down Mutual Fund Analysis API")

@app.get("/", response_model=Dict)
async def root():
    """Health check endpoint"""
    return {
        "message": "Mutual Fund Analysis API", 
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        service="Mutual Fund Analysis API",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_mutual_fund(request: MutualFundRequest):
    """
    Analyze a mutual fund and generate comprehensive report
    """
    try:
        fund_name = request.mutual_fund_name.strip()
        
        if not fund_name:
            raise HTTPException(status_code=400, detail="Mutual fund name is required")
        
        if len(fund_name) < 3:
            raise HTTPException(status_code=400, detail="Fund name too short. Please provide the complete fund name.")
        
        logger.info(f"Starting analysis for: {fund_name}")
        
        # Run all analyses concurrently
        tasks = [
            analyzer.analyze_mutual_fund(fund_name),
            analyzer.analyze_sentiment(fund_name),
            analyzer.analyze_macroeconomic(fund_name)
        ]
        
        # Execute all analyses in parallel
        fund_analysis, sentiment_analysis, macro_analysis = await asyncio.gather(*tasks)
        
        # Generate final report
        final_report = await analyzer.compile_final_report(
            fund_name, fund_analysis, sentiment_analysis, macro_analysis
        )
        
        # Compile response
        analysis_result = {
            "fund_analysis": fund_analysis,
            "sentiment_analysis": sentiment_analysis,
            "macroeconomic_analysis": macro_analysis,
            "final_report": final_report
        }
        
        logger.info(f"Analysis completed for: {fund_name}")
        
        return AnalysisResponse(
            status="success",
            fund_name=fund_name,
            analysis=analysis_result,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-async")
async def analyze_mutual_fund_async(request: MutualFundRequest, background_tasks: BackgroundTasks):
    """
    Start async analysis (for long-running analyses)
    """
    fund_name = request.mutual_fund_name.strip()
    
    if not fund_name:
        raise HTTPException(status_code=400, detail="Mutual fund name is required")
    
    # Generate a simple task ID
    task_id = f"task_{int(datetime.now().timestamp())}"
    
    # Add background task
    background_tasks.add_task(run_background_analysis, fund_name, task_id)
    
    return {
        "status": "accepted",
        "task_id": task_id,
        "fund_name": fund_name,
        "message": "Analysis started. Results will be processed in the background."
    }

async def run_background_analysis(fund_name: str, task_id: str):
    """Background task for analysis"""
    logger.info(f"Background analysis started for {fund_name} (Task: {task_id})")
    
    try:
        # Run the same analysis as the sync version
        tasks = [
            analyzer.analyze_mutual_fund(fund_name),
            analyzer.analyze_sentiment(fund_name),
            analyzer.analyze_macroeconomic(fund_name)
        ]
        
        fund_analysis, sentiment_analysis, macro_analysis = await asyncio.gather(*tasks)
        
        final_report = await analyzer.compile_final_report(
            fund_name, fund_analysis, sentiment_analysis, macro_analysis
        )
        
        # In production, store results in database or cache
        logger.info(f"Background analysis completed for {fund_name} (Task: {task_id})")
        
    except Exception as e:
        logger.error(f"Background analysis failed for {fund_name} (Task: {task_id}): {str(e)}")

@app.get("/analyze")
async def analyze_get_info():
    """Information about the analyze endpoint"""
    return {
        "message": "This endpoint requires a POST request with JSON data",
        "method": "POST",
        "url": "/analyze",
        "example_request": {
            "mutual_fund_name": "HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan"
        },
        "curl_example": 'curl -X POST "YOUR_PRODUCTION_URL/analyze" -H "Content-Type: application/json" -d \'{"mutual_fund_name": "HDFC Top 100 Fund"}\'',
        "interactive_docs": "Visit /docs for interactive API testing"
    }

@app.get("/example")
async def get_example():
    """Get example request format"""
    return {
        "example_request": {
            "mutual_fund_name": "HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan"
        },
        "popular_funds": [
            "HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan",
            "SBI Small Cap Fund - Direct Plan - Growth",
            "Axis Bluechip Fund - Direct Plan - Growth",
            "Mirae Asset Large Cap Fund - Direct Plan - Growth",
            "Parag Parikh Long Term Equity Fund - Direct Plan - Growth"
        ],
        "endpoints": {
            "analyze": "POST /analyze - Synchronous analysis",
            "analyze-async": "POST /analyze-async - Asynchronous analysis",
            "health": "GET /health - Service health check",
            "docs": "GET /docs - Interactive API documentation"
        }
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
