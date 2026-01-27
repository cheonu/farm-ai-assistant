import openai
import os 
import dotenv
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class FarmLLMService:
    def __init__(self):
        """ Initialize the LLM service with OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: 
            raise ValueError("OPENAI_API_KEY env var is required")
        self.client = openai.OpenAI(api_key=api_key)
        self.conversations = {}

    def create_farm_system_prompt(self) -> str:
        """Create the system prompt that defines the AI's role"""
        return """You are an expert pig farm management assistant with deep knowledge of:

EXPERTISE AREAS:
- Pig breeding cycles and reproductive management
- Gestation periods (114 days for pigs)
- Heat cycles (21-day average cycle)
- Health monitoring and disease prevention
- Feed management and nutrition optimization
- Farm operations and efficiency analysis

RESPONSE STYLE:
- Provide practical, actionable advice based on the specific farm data
- Always cite specific data points from the farm when making recommendations
- Be concise but thorough in explanations
- If you need more information, ask specific questions
- Use farming terminology appropriately
- Focus on solutions and improvements

FARM DATA CONTEXT:
You have access to real-time farm data including:
- Pig inventory (sows, boars, gilts, growers, piglets)
- Breeding records (crossing dates, expected delivery dates)
- Health records (medications, treatments)
- Individual pig tracking by tag numbers

Always base your responses on the actual data provided, not general assumptions."""

    def format_farm_context(self, farm_data: Dict) -> str:
        """ Convert Farm data into LLM friendly context """
        if not farm_data or not farm_data.get("pigs"):
            return "No farm data provided."
        
        pigs = farm_data.get("pigs", [])
        context_parts = []

        total_pigs = len(pigs)
        context_parts.append(f"FARM OVERVIEW:\nTotal Pigs: {total_pigs}")

        gender_counts = {}
        pregnant_pigs = []
        overdue_pigs = []
        recent_medications = []

        today = datetime.now()

        for pig in pigs:
            gender = pig.get("gender", "Unknown")
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            # crossed pigs
            if pig.get("crossedDate") and pig.get("expectedDeliveryDate"):
                pregnant_pigs.append(pig)

                #overdue pig
                try:
                    expected_date = datetime.fromisoformat(pig['expectedDeliveryDate'].replace('Z', ''))
                    if today > expected_date:
                        days_overdue = (today - expected_date).days 
                        overdue_pigs.append({
                            "tag": pig.get("tag_number", pig.get("tagNumber")),
                            "days_overdue": days_overdue
                        })
                except: 
                    pass
            # Track recent medications
            medications = pig.get('medications', [])
            if medications:
                for med in medications[-2:]:  # Last 2 medications
                    recent_medications.append({
                        'pig': pig.get('tagNumber', pig.get('tag_number')),
                        'medication': med.get('name'),
                        'date': med.get('date')
                    })

        gender_summary = ", ".join([f"{gender}: {count})" for gender, count in gender_counts.items()])
        context_parts.append(f"Gender Distribution {gender_summary}")

        # Add breeding information
        context_parts.append(f"\nBREEDING STATUS:")
        context_parts.append(f"Pregnant Pigs: {len(pregnant_pigs)}")

        if overdue_pigs:
            context_parts.append(f"Overdue Farrowings: {len(overdue_pigs)}")
            for pig in overdue_pigs[:3]:
                context_parts.append(f"  - Pig {pig['tag']}: {pig['days_overdue']} days overdue")

        # Add health information
        if recent_medications:
            context_parts.append(f"\nRECENT HEALTH ACTIVITY:")
            for med in recent_medications[:5]:
                context_parts.append(f"  - Pig {med['pig']}: {med['medication']} on {med['date']}")

        return "\n".join(context_parts)

    async def ask_question(self, question: str, farm_context: Dict, conversation_id: Optional[str] = None) -> Dict:
        """Process a farm management question using AI"""

        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = []

        # Format the farm data context
        context_text = self.format_farm_context(farm_context)

        messages = [
                {"role": "system", "content": self.create_farm_system_prompt()},
                {"role": "user", "content": f"CURRENT FARM DATA:\n{context_text}\n\nQUESTION: {question}"}
        ]

        # Add recent conversation history (last 4 messages)
        conversation_history = self.conversations[conversation_id][-4:]
        for msg in conversation_history:
                messages.append(msg)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=600,
                presence_penalty=0.1
            )

            answer = response.choices[0].message.content
            self.conversations[conversation_id].extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])

            # Keep conversation history manageable (last 10 messages)
            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[conversation_id][-10:]
            
            return {
                "answer": answer,
                "confidence": 0.8,
                "sources": [],
                "conversation_id": conversation_id
            }
        except Exception as e:
            return {
                "answer": f"I'm sorry, I encountered an error processing your question: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "conversation_id": conversation_id
            }
    async def analyze_farm_performance(self, farm_data: Dict) -> Dict:
        """Provide comprehensive farm performance analysis"""

        context_text = self.format_farm_context(farm_data)

        analysis_prompt = f"""
Based on the following farm data, provide a comprehensive performance analysis:

{context_text}

Please analyze and provide insights on:
1. BREEDING EFFICIENCY: Are breeding cycles optimized? Any concerns?
2. HERD COMPOSITION: Is the gender/age balance appropriate?
3. HEALTH STATUS: Any patterns in medication usage or health issues?
4. OPERATIONAL ALERTS: Immediate actions needed (overdue farrowings, etc.)
5. RECOMMENDATIONS: Specific actionable improvements

Format your response with clear sections and specific data-driven recommendations.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.create_farm_system_prompt()},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=800,
                temperature=0.3  # Lower temperature for more focused analysis
            )
            return {
                "analysis": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat(),
                "data_points_analyzed": len(farm_data.get('pigs', [])),
                "status": "success"
            }
        except Exception as e:
            return {
                "analysis": f"Error analyzing farm performance: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "data_points_analyzed": 0,
                "status": "error"
            }