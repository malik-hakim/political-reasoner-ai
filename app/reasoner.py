# app/reasoner.py - Enhanced dengan user-friendly error handling
import json
import time
import logging
from .openai_manager import OpenAIManager
from .prompts import PromptTemplates
from .utils import (
    retry_with_exponential_backoff, 
    PoliticalReasonerError, 
    UserFriendlyError,
    safe_json_parse, 
    validate_openai_response, 
    clean_text, 
    format_analysis_response,
    parse_openai_error,
    validate_input_data
)

logger = logging.getLogger(__name__)

class PoliticalReasoner:
    def __init__(self):
        try:
            self.openai = OpenAIManager()
            self.prompts = PromptTemplates()
            logger.info("PoliticalReasoner initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PoliticalReasoner: {e}")
            raise UserFriendlyError(
                "🔧 Gagal menginisialisasi sistem AI. Silakan hubungi administrator.",
                f"Initialization error: {str(e)}"
            )

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1)
    def _make_openai_request(self, messages, temperature=0.7, max_tokens=1500):
        """Make request to OpenAI dengan enhanced error handling"""
        try:
            logger.info(f"Making OpenAI request with {len(messages)} messages")
            
            # Validate messages
            if not messages or not isinstance(messages, list):
                raise UserFriendlyError(
                    "🤖 Format permintaan tidak valid.",
                    "Invalid messages format"
                )
            
            response = self.openai.client.chat.completions.create(
                model=self.openai.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = validate_openai_response(response)
            logger.info("OpenAI request successful")
            return content
            
        except UserFriendlyError:
            raise
        except Exception as e:
            # Parse OpenAI specific errors
            user_msg, suggestion = parse_openai_error(str(e))
            logger.error(f"OpenAI API error: {str(e)}")
            raise UserFriendlyError(user_msg, str(e))

    def analyze_political_text(self, text: str):
        """Analisis teks politik dengan comprehensive error handling"""
        try:
            # Validate input
            validate_input_data({'text': text}, ['text'])
            text = clean_text(text)
            
            logger.info(f"Analyzing political text ({len(text)} characters)")
            
            # Prepare prompt
            prompt = self.prompts.get_political_analysis_prompt(text)
            messages = [
                {"role": "system", "content": "Anda adalah analis politik Indonesia yang ahli dan objektif."},
                {"role": "user", "content": prompt}
            ]
            
            # Make request
            response = self._make_openai_request(messages)
            
            # Parse response
            if response.strip().startswith("{"):
                try:
                    parsed_response = json.loads(response)
                    return format_analysis_response(parsed_response)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error, using structured response: {e}")
                    return self._structure_response(response)
            else:
                return self._structure_response(response)
                
        except UserFriendlyError as e:
            logger.error(f"User-friendly error in analyze_political_text: {e.user_message}")
            return {
                "error": e.user_message,
                "status": "error",
                "error_type": "user_friendly"
            }
        except Exception as e:
            logger.error(f"Unexpected error in analyze_political_text: {e}")
            return {
                "error": "🤖 Terjadi kesalahan tak terduga saat menganalisis teks. Silakan coba lagi.",
                "status": "error",
                "error_type": "unexpected",
                "technical_error": str(e)
            }

    def _structure_response(self, response: str):
        """Structure unformatted response dengan error handling"""
        try:
            logger.info("Structuring unformatted response")
            
            if not response or response.strip() == "":
                return {
                    "error": "🤖 AI memberikan respons kosong. Silakan coba dengan teks yang berbeda.",
                    "status": "error"
                }
            
            return {
                "sentiment": {"label": "netral", "score": 0.5},
                "topics": self._extract_topics_from_text(response),
                "entities": self._extract_entities_from_text(response),
                "key_issues": self._extract_issues_from_text(response),
                "bias_detected": False,
                "public_impact": "medium",
                "raw_analysis": response,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error structuring response: {e}")
            return {
                "error": "🔧 Gagal memproses hasil analisis. Format respons tidak valid.",
                "status": "error"
            }

    def _extract_topics_from_text(self, text: str):
        """Extract topics dengan error handling"""
        try:
            political_keywords = {
                "ekonomi": ["ekonomi", "keuangan", "investasi", "bisnis", "perdagangan", "inflasi", "pajak"],
                "politik": ["politik", "partai", "pemilu", "demokrasi", "kekuasaan", "pemerintah"],
                "sosial": ["sosial", "masyarakat", "rakyat", "warga", "komunitas", "budaya"],
                "hukum": ["hukum", "regulasi", "kebijakan", "peraturan", "undang-undang", "yuridis"],
                "teknologi": ["digital", "teknologi", "internet", "sistem", "platform", "cyber"],
                "pendidikan": ["pendidikan", "sekolah", "universitas", "mahasiswa", "guru", "kurikulum"],
                "kesehatan": ["kesehatan", "rumah sakit", "dokter", "obat", "vaksin", "medis"],
                "lingkungan": ["lingkungan", "iklim", "polusi", "hutan", "energi", "sampah"]
            }
            
            text_lower = text.lower()
            found_topics = []
            
            for topic, keywords in political_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    found_topics.append(topic)
            
            return found_topics[:5] if found_topics else ["umum"]
            
        except Exception as e:
            logger.warning(f"Error extracting topics: {e}")
            return ["umum"]

    def _extract_entities_from_text(self, text: str):
        """Extract entities dengan error handling"""
        try:
            entities = []
            words = text.split()
            
            for i, word in enumerate(words):
                if len(word) > 2 and word[0].isupper():
                    # Skip common words
                    skip_words = ['Dalam', 'Untuk', 'Dengan', 'Dari', 'Pada', 'Yang', 'Akan', 'Telah']
                    if word not in skip_words:
                        if i < len(words) - 1 and words[i + 1][0].isupper():
                            entities.append(f"{word} {words[i + 1]}")
                        else:
                            entities.append(word)
            
            return list(set(entities))[:10] if entities else []
            
        except Exception as e:
            logger.warning(f"Error extracting entities: {e}")
            return []

    def _extract_issues_from_text(self, text: str):
        """Extract issues dengan error handling"""
        try:
            issue_keywords = [
                "masalah", "tantangan", "kendala", "hambatan", "isu", 
                "persoalan", "kesulitan", "problem", "krisis", "konflik"
            ]
            
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            issues = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in issue_keywords):
                    if len(sentence) > 20:  # Only meaningful sentences
                        issues.append(sentence)
            
            return issues[:5] if issues else []
            
        except Exception as e:
            logger.warning(f"Error extracting issues: {e}")
            return []

    def extract_key_insights(self, analysis: dict):
        """Extract insights dengan error handling"""
        try:
            if "error" in analysis:
                return {
                    "error": analysis["error"],
                    "status": "error"
                }
            
            logger.info("Extracting key insights")
            
            insights = {
                "sentiment_summary": analysis.get("sentiment", {"label": "netral", "score": 0.5}),
                "main_topics": analysis.get("topics", [])[:3],
                "political_entities": analysis.get("entities", [])[:5],
                "critical_issues": analysis.get("key_issues", [])[:3],
                "impact_level": analysis.get("public_impact", "medium"),
                "bias_detected": analysis.get("bias_detected", False),
                "timestamp": analysis.get("timestamp", time.time()),
                "status": "success"
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {
                "error": "🔍 Gagal mengekstrak insight dari hasil analisis.",
                "status": "error"
            }

    def generate_narrative(self, analysis_data: dict):
        """Generate narrative dengan error handling"""
        try:
            if "error" in analysis_data:
                return {
                    "error": analysis_data["error"],
                    "status": "error"
                }
            
            logger.info("Generating narrative")
            
            prompt = self.prompts.get_narrative_generation_prompt(analysis_data)
            messages = [
                {"role": "system", "content": "Anda adalah jurnalis politik yang objektif dan berpengalaman."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._make_openai_request(messages, temperature=0.8, max_tokens=800)
            
            if not response or len(response.strip()) < 50:
                return {
                    "error": "📝 Narasi yang dihasilkan terlalu pendek atau kosong. Silakan coba lagi.",
                    "status": "error"
                }
            
            return {
                "narrative": response,
                "status": "success"
            }
            
        except UserFriendlyError as e:
            logger.error(f"User-friendly error in generate_narrative: {e.user_message}")
            return {
                "error": e.user_message,
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in generate_narrative: {e}")
            return {
                "error": "📝 Gagal menghasilkan narasi analisis. Silakan coba lagi.",
                "status": "error"
            }

    def generate_policy_recommendations(self, context: str, issue: str):
        """Generate policy recommendations dengan error handling"""
        try:
            # Validate inputs
            validate_input_data({'context': context, 'issue': issue}, ['context', 'issue'])
            
            context = clean_text(context)
            issue = clean_text(issue)
            
            logger.info(f"Generating policy recommendations for: {issue}")
            
            prompt = self.prompts.get_policy_recommendation_prompt(context, issue)
            messages = [
                {"role": "system", "content": "Anda adalah konsultan kebijakan publik yang berpengalaman di Indonesia."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._make_openai_request(messages, max_tokens=1200)
            
            # Try to parse as JSON first
            if response.strip().startswith("{"):
                try:
                    parsed = json.loads(response)
                    parsed["status"] = "success"
                    return parsed
                except json.JSONDecodeError:
                    pass
            
            # Fallback structure
            return {
                "recommendations": [response] if response else ["Tidak ada rekomendasi yang dapat dihasilkan"],
                "implementation_timeline": {
                    "phase_1": "1-3 bulan", 
                    "phase_2": "3-6 bulan",
                    "phase_3": "6-12 bulan"
                },
                "stakeholders": ["Pemerintah", "DPR", "Masyarakat", "Swasta"],
                "potential_challenges": ["Anggaran", "Koordinasi", "Implementasi", "Regulasi"],
                "status": "success"
            }
            
        except UserFriendlyError as e:
            logger.error(f"User-friendly error in generate_policy_recommendations: {e.user_message}")
            return {
                "error": e.user_message,
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in generate_policy_recommendations: {e}")
            return {
                "error": "💡 Gagal menghasilkan rekomendasi kebijakan. Silakan coba lagi dengan konteks yang lebih jelas.",
                "status": "error"
            }

    def chat_response(self, question: str, context: dict = None):
        """Generate chat response dengan error handling"""
        try:
            # Validate input
            validate_input_data({'question': question}, ['question'])
            question = clean_text(question)
            
            logger.info(f"Processing chat question: {question[:50]}...")
            
            system_msg = "Anda adalah asisten AI ahli politik Indonesia yang membantu menganalisis dan menjelaskan isu politik dengan objektif dan mudah dipahami."
            messages = [{"role": "system", "content": system_msg}]
            
            # Add context if available
            if context and not context.get("error"):
                try:
                    context_msg = f"Konteks analisis sebelumnya: {json.dumps(context, ensure_ascii=False)}"
                    messages.append({"role": "user", "content": context_msg})
                except Exception as e:
                    logger.warning(f"Error adding context: {e}")
            
            messages.append({"role": "user", "content": question})
            
            response = self._make_openai_request(messages, temperature=0.7, max_tokens=1000)
            
            if not response or len(response.strip()) < 10:
                return {
                    "error": "🤖 Respons AI terlalu pendek atau kosong. Silakan ajukan pertanyaan yang lebih spesifik.",
                    "status": "error"
                }
            
            return {
                "response": response,
                "status": "success"
            }
            
        except UserFriendlyError as e:
            logger.error(f"User-friendly error in chat_response: {e.user_message}")
            return {
                "error": e.user_message,
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in chat_response: {e}")
            return {
                "error": "💬 Gagal memproses pertanyaan Anda. Silakan coba dengan pertanyaan yang lebih sederhana.",
                "status": "error"
            }
