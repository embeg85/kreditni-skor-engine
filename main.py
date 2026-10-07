from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Alternative Credit Scoring API")

# Definisanje strukture podataka koje API očekuje da primi
class StripeData(BaseModel):
    mjesecni_prihodi: List[float]
    broj_aktivnih_klijenata: int

class YoutubeData(BaseModel):
    broj_pretplatnika: int
    pregledi_zadnjih_30_dana: int
    trend_rasta_pregleda: float

class ScoringRequest(BaseModel):
    stripe: StripeData
    youtube: YoutubeData

@app.get("/")
def home():
    return {"status": "API radi uživo!", "poruka": "Pošalji POST zahtjev na /izracunaj-skor"}

@app.post("/izracunaj-skor")
def izracunaj_kreditni_skor(data: ScoringRequest):
    skor = 50
    
    # 1. ANALIZA PRIHODA (Stripe)
    mjesecni_prihodi = data.stripe.mjesecni_prihodi
    broj_klijenata = data.stripe.broj_aktivnih_klijenata
    
    if not mjesecni_prihodi:
        return {"kreditni_skor": 0, "poruka": "Nema prihoda."}
        
    prosjek = sum(mjesecni_prihodi) / len(mjesecni_prihodi)
    
    if broj_klijenata >= 4:
        skor += 15
    elif broj_klijenata == 1:
        skor -= 15
        
    nagli_pad = False
    for i in range(1, len(mjesecni_prihodi)):
        if mjesecni_prihodi[i] < mjesecni_prihodi[i-1] * 0.60:
            nagli_pad = True
            break
            
    if nagli_pad:
        skor -= 15
    else:
        skor += 15

    # 2. ANALIZA YOUTUBE METRIKA
    if data.youtube.broj_pretplatnika > 50000:
        skor += 10
    elif data.youtube.broj_pretplatnika > 10000:
        skor += 5
        
    if data.youtube.trend_rasta_pregleda > 0.05:
        skor += 10
    elif data.youtube.trend_rasta_pregleda < -0.20:
        skor -= 10

    # 3. LIMITI I KLASIFIKACIJA
    finalni_skor = max(1, min(100, skor))
    
    if finalni_skor >= 80:
        klasa = "A (Odličan - Nizak rizik)"
    elif finalni_skor >= 60:
        klasa = "B (Dobar - Srednji rizik)"
    elif finalni_skor >= 40:
        klasa = "C (Zadovoljavajući)"
    else:
        klasa = "D (Visok rizik)"
        
    return {
        "kreditni_skor": finalni_skor,
        "kreditna_klasa": klasa,
        "analiza": {
            "prosjecan_prihod": round(prosjek, 2),
            "rizik_jednog_klijenta": "Visok" if broj_klijenata == 1 else "Nizak",
            "trend_publike": "U padu" if data.youtube.trend_rasta_pregleda < 0 else "Stabilan/U rastu"
        }
    }
