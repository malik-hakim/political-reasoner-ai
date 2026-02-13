import json

class PromptTemplates:
    @staticmethod
    def get_political_analysis_prompt(text: str) -> str:
        return f"""Analisis teks politik berikut dan berikan insight mendalam:

Teks: "{text}"

Berikan analisis dalam format berikut:
1. Sentiment keseluruhan (positif/negatif/netral) dengan score 0-1
2. Topik utama yang dibahas (maksimal 5 topik)
3. Entitas politik yang disebutkan (nama, partai, jabatan)
4. Isu-isu kunci yang diangkat
5. Bias politik yang terdeteksi (jika ada)
6. Dampak potensial terhadap opini publik

Format JSON yang clean dan terstruktur.
"""

    @staticmethod
    def get_narrative_generation_prompt(analysis_data: dict) -> str:
        return f"""Berdasarkan data analisis politik berikut:
{json.dumps(analysis_data, indent=2)}

Generate narasi pendek (150-200 kata) yang menjelaskan:
- Ringkasan insight utama
- Implikasi politik yang mungkin terjadi
- Rekomendasi untuk stakeholder terkait

Narasi harus objektif, informatif, dan mudah dipahami.
"""

    @staticmethod
    def get_policy_recommendation_prompt(context: str, issue: str) -> str:
        return f"""Konteks: {context}
Isu: {issue}

Berikan rekomendasi kebijakan yang:
1. Praktis dan dapat diimplementasikan
2. Berdasarkan best practices internasional
3. Sesuai konteks politik Indonesia
4. Sertakan timeline implementasi
5. Identifikasi stakeholder utama

Format JSON:
- recommendations: []
- implementation_timeline: {{}}
- stakeholders: []
- potential_challenges: []
"""
