import time
import json
import logging
import functools
import random
import re

# Setup logging
logger = logging.getLogger(__name__)

class UserFriendlyError(Exception):
    """Custom exception dengan pesan user-friendly"""
    def __init__(self, user_message, technical_message=None, error_code=None):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        self.error_code = error_code
        super().__init__(self.technical_message)

def parse_openai_error(error_str):
    """Parse OpenAI error dan return user-friendly message"""
    error_lower = error_str.lower()
    
    # Error patterns dan user-friendly messages
    error_patterns = {
        'insufficient_quota': {
            'message': '🚫 Kuota API OpenAI telah habis. Silakan hubungi administrator untuk mengisi ulang kuota.',
            'suggestion': 'Coba lagi dalam beberapa saat atau hubungi tim teknis.'
        },
        'rate_limit': {
            'message': '⏳ Terlalu banyak permintaan dalam waktu singkat. Mohon tunggu sebentar.',
            'suggestion': 'Silakan coba lagi dalam 1-2 menit.'
        },
        'invalid_api_key': {
            'message': '🔑 Konfigurasi API tidak valid. Silakan hubungi administrator.',
            'suggestion': 'Tim teknis perlu memeriksa pengaturan API.'
        },
        'model_not_found': {
            'message': '🤖 Model AI tidak tersedia saat ini.',
            'suggestion': 'Coba lagi nanti atau hubungi support.'
        },
        'context_length_exceeded': {
            'message': '📝 Teks yang dianalisis terlalu panjang.',
            'suggestion': 'Coba dengan teks yang lebih pendek (maksimal 5000 karakter).'
        },
        'server_error': {
            'message': '🔧 Server OpenAI mengalami gangguan sementara.',
            'suggestion': 'Silakan coba lagi dalam beberapa menit.'
        },
        'timeout': {
            'message': '⏱️ Waktu analisis habis. Koneksi mungkin lambat.',
            'suggestion': 'Periksa koneksi internet dan coba lagi.'
        },
        'network_error': {
            'message': '🌐 Masalah koneksi internet terdeteksi.',
            'suggestion': 'Periksa koneksi internet Anda dan coba lagi.'
        }
    }
    
    # Check for specific error patterns
    for pattern, info in error_patterns.items():
        if pattern in error_lower or str(pattern) in error_lower:
            return info['message'], info['suggestion']
    
    # Check for HTTP status codes
    if '429' in error_str:
        return error_patterns['rate_limit']['message'], error_patterns['rate_limit']['suggestion']
    elif '500' in error_str or '502' in error_str or '503' in error_str:
        return error_patterns['server_error']['message'], error_patterns['server_error']['suggestion']
    elif '401' in error_str or '403' in error_str:
        return error_patterns['invalid_api_key']['message'], error_patterns['invalid_api_key']['suggestion']
    
    # Default fallback
    return ('🤖 Sistem AI mengalami kendala teknis sementara.', 
            'Silakan coba lagi dalam beberapa menit atau hubungi support jika masalah berlanjut.')

def retry_with_exponential_backoff(max_retries=3, initial_delay=1, exponential_base=2, jitter=True):
    """Decorator untuk retry dengan exponential backoff dan user-friendly errors"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Parse error untuk user-friendly message
                    user_msg, suggestion = parse_openai_error(str(e))
                    
                    # Check if it's a retryable error
                    retryable_errors = ['rate_limit', '429', 'quota', 'server_error', '500', '502', '503', 'timeout']
                    is_retryable = any(err in error_msg for err in retryable_errors)
                    
                    if is_retryable and attempt < max_retries - 1:
                        sleep_time = delay
                        if jitter:
                            sleep_time += random.uniform(0, delay * 0.1)
                        
                        logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries}): {user_msg}")
                        time.sleep(sleep_time)
                        delay *= exponential_base
                        continue
                    else:
                        # For non-retryable errors or final attempt
                        logger.error(f"Final error: {str(e)}")
                        raise UserFriendlyError(user_msg, str(e))
            
            # If we get here, all retries failed
            user_msg, suggestion = parse_openai_error(str(last_exception))
            raise UserFriendlyError(
                f"{user_msg} Sudah dicoba {max_retries} kali.", 
                str(last_exception)
            )
            
        return wrapper
    return decorator

class PoliticalReasonerError(Exception):
    """Custom exception untuk Political Reasoner dengan user-friendly messages"""
    def __init__(self, user_message, technical_message=None):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        super().__init__(self.technical_message)

def safe_json_parse(text):
    """Safely parse JSON with fallback"""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        return {"text": text, "parsed": False, "error": "Format respons tidak valid"}

def validate_openai_response(response):
    """Validate OpenAI API response dengan error handling"""
    try:
        if not response:
            raise UserFriendlyError(
                "🤖 AI tidak memberikan respons. Silakan coba lagi.",
                "Empty response from OpenAI"
            )
        
        if not hasattr(response, 'choices') or not response.choices:
            raise UserFriendlyError(
                "🤖 Format respons AI tidak valid. Silakan coba lagi.",
                "No choices in OpenAI response"
            )
        
        if not response.choices[0].message:
            raise UserFriendlyError(
                "🤖 Pesan dari AI kosong. Silakan coba lagi.",
                "No message in OpenAI response"
            )
        
        content = response.choices[0].message.content
        if not content or content.strip() == "":
            raise UserFriendlyError(
                "🤖 AI memberikan respons kosong. Silakan coba lagi dengan teks yang berbeda.",
                "Empty content in OpenAI response"
            )
        
        return content
        
    except UserFriendlyError:
        raise
    except Exception as e:
        raise UserFriendlyError(
            "🤖 Terjadi kesalahan saat memproses respons AI.",
            f"Response validation error: {str(e)}"
        )

def clean_text(text):
    """Clean and validate input text dengan error handling"""
    try:
        if not text:
            raise UserFriendlyError(
                "📝 Teks tidak boleh kosong. Silakan masukkan teks untuk dianalisis.",
                "Empty text input"
            )
        
        if not isinstance(text, str):
            text = str(text)
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Length validation
        if len(text) < 10:
            raise UserFriendlyError(
                "📝 Teks terlalu pendek. Minimal 10 karakter untuk analisis yang akurat.",
                f"Text too short: {len(text)} characters"
            )
        
        if len(text) > 10000:
            logger.warning(f"Text truncated from {len(text)} to 10000 characters")
            text = text[:10000] + "..."
        
        return text.strip()
        
    except UserFriendlyError:
        raise
    except Exception as e:
        raise UserFriendlyError(
            "📝 Gagal memproses teks input. Periksa format teks Anda.",
            f"Text cleaning error: {str(e)}"
        )

def format_analysis_response(analysis_data):
    """Format analysis response dengan error handling"""
    try:
        if not analysis_data:
            return {
                "sentiment": {"label": "netral", "score": 0.5},
                "topics": [],
                "entities": [],
                "key_issues": [],
                "bias_detected": False,
                "public_impact": "medium",
                "timestamp": time.time(),
                "status": "success"
            }
        
        # Ensure required keys exist dengan default values
        formatted = {
            "sentiment": analysis_data.get("sentiment", {"label": "netral", "score": 0.5}),
            "topics": analysis_data.get("topics", []),
            "entities": analysis_data.get("entities", []),
            "key_issues": analysis_data.get("key_issues", []),
            "bias_detected": analysis_data.get("bias_detected", False),
            "public_impact": analysis_data.get("public_impact", "medium"),
            "timestamp": analysis_data.get("timestamp", time.time()),
            "status": "success"
        }
        
        return formatted
        
    except Exception as e:
        logger.error(f"Error formatting analysis response: {e}")
        return {
            "error": "Gagal memformat hasil analisis",
            "status": "error",
            "timestamp": time.time()
        }

def handle_api_connection_error():
    """Handle API connection errors"""
    return {
        "error": "🌐 Tidak dapat terhubung ke layanan AI. Periksa koneksi internet Anda.",
        "suggestion": "Pastikan koneksi internet stabil dan coba lagi dalam beberapa saat.",
        "status": "connection_error"
    }

def validate_input_data(data, required_fields):
    """Validate input data dengan user-friendly messages"""
    try:
        if not data:
            raise UserFriendlyError(
                "📋 Data input kosong. Silakan isi form dengan lengkap.",
                "Empty input data"
            )
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            field_names = {
                'text': 'Teks untuk analisis',
                'question': 'Pertanyaan',
                'context': 'Konteks',
                'issue': 'Isu politik'
            }
            
            missing_names = [field_names.get(field, field) for field in missing_fields]
            raise UserFriendlyError(
                f"📋 Field berikut harus diisi: {', '.join(missing_names)}",
                f"Missing required fields: {missing_fields}"
            )
        
        return True
        
    except UserFriendlyError:
        raise
    except Exception as e:
        raise UserFriendlyError(
            "📋 Gagal memvalidasi data input.",
            f"Input validation error: {str(e)}"
        )


