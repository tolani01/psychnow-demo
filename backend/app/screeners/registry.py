"""
Screener Registry
Factory for accessing all screener implementations
"""
from typing import Dict, Type, List
from app.screeners.base import BaseScreener
from app.screeners.depression.phq9 import PHQ9
from app.screeners.anxiety.gad7 import GAD7
from app.screeners.suicide.cssrs import CSSRS
from app.screeners.adhd.asrs import ASRS
from app.screeners.trauma.pcl5 import PCL5
from app.screeners.sleep.isi import ISI
from app.screeners.substance.audit_c import AUDITC
from app.screeners.substance.dast10 import DAST10
from app.screeners.bipolar.mdq import MDQ
from app.screeners.eating.scoff import SCOFF
from app.screeners.ocd.ocir import OCIR
from app.screeners.stress.pss10 import PSS10
from app.screeners.anxiety.spin import SPIN
# New screeners - Batch 2
from app.screeners.somatic.phq15 import PHQ15
from app.screeners.functioning.whodas import WHODAS
from app.screeners.anxiety.pdss import PDSS
from app.screeners.substance.cage_aid import CAGEAID
from app.screeners.functioning.wsas import WSAS
from app.screeners.trauma.pc_ptsd import PCPTSD5
from app.screeners.perinatal.epds import EPDS
from app.screeners.trauma.ctq_sf import CTQSF
from app.screeners.depression.phq2 import PHQ2
from app.screeners.anxiety.gad2 import GAD2
from app.screeners.anxiety.pswq8 import PSWQ8
from app.screeners.stress.pss4 import PSS4
from app.screeners.quality_of_life.ucla3 import UCLA3
from app.screeners.quality_of_life.swls import SWLS
from app.screeners.impulsivity.bis15 import BIS15
from app.screeners.cognition.rrs10 import RRS10

import re as _re

def parse_screener_options(text: str) -> list:
    """
    Parse options from screener question text.
    Looks for BEGIN_OPTIONS/END_OPTIONS blocks.
    
    Returns:
        List of dicts with {label, value, code}
    """
    if not text:
        return []
    
    lowered = text.lower()
    s = lowered.find("begin_options")
    e = lowered.find("end_options")
    
    if s != -1 and e != -1 and e > s:
        block = text[s + len("begin_options"):e]
    else:
        block = text
    
    items = []
    for line in block.splitlines():
        line = line.strip()
        if _re.match(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", line):
            item = _re.sub(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", "", line).strip()
            if item:
                items.append(item)
    
    # Deduplicate
    seen = set()
    cleaned = []
    for it in items:
        k = it.lower()
        if k in seen:
            continue
        seen.add(k)
        cleaned.append(it)
    
    # Create code slugs
    def slug(s: str) -> str:
        s = s.lower().strip()
        s = _re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:40] or "option"
    
    return [{"label": it, "value": it, "code": slug(it)} for it in cleaned]


class ScreenerRegistry:
    """Registry of all available screeners"""
    
    _screeners: Dict[str, Type[BaseScreener]] = {
        # Core screeners (13)
        "PHQ-9": PHQ9,
        "GAD-7": GAD7,
        "C-SSRS": CSSRS,
        "ASRS": ASRS,
        "PCL-5": PCL5,
        "ISI": ISI,
        "AUDIT-C": AUDITC,
        "DAST-10": DAST10,
        "MDQ": MDQ,
        "SCOFF": SCOFF,
        "OCI-R": OCIR,
        "PSS-10": PSS10,
        "SPIN": SPIN,
        # New screeners - Batch 2 (17)
        "PHQ-15": PHQ15,           # Somatic symptoms
        "WHODAS 2.0": WHODAS,      # Functioning/disability
        "PDSS": PDSS,              # Panic disorder severity
        "CAGE-AID": CAGEAID,       # Substance abuse brief
        "WSAS": WSAS,              # Work/social adjustment
        "PC-PTSD-5": PCPTSD5,      # PTSD brief
        "EPDS": EPDS,              # Perinatal depression
        "CTQ-SF": CTQSF,           # Childhood trauma
        "PHQ-2": PHQ2,             # Depression brief
        "GAD-2": GAD2,             # Anxiety brief
        "PSWQ-8": PSWQ8,           # Worry
        "PSS-4": PSS4,             # Stress brief
        "UCLA-3": UCLA3,           # Loneliness
        "SWLS": SWLS,              # Life satisfaction
        "BIS-15": BIS15,           # Impulsivity
        "RRS-10": RRS10,           # Rumination
    }
    
    @classmethod
    def get_screener(cls, name: str) -> BaseScreener:
        """
        Get a screener instance by name
        
        Args:
            name: Screener name (e.g., "PHQ-9")
            
        Returns:
            Screener instance
            
        Raises:
            ValueError: If screener not found
        """
        screener_class = cls._screeners.get(name)
        if screener_class is None:
            raise ValueError(f"Screener '{name}' not found. Available: {list(cls._screeners.keys())}")
        
        return screener_class()
    
    @classmethod
    def list_screeners(cls) -> List[str]:
        """Get list of all available screener names"""
        return list(cls._screeners.keys())
    
    @classmethod
    def get_screeners_for_symptoms(cls, symptoms: Dict[str, bool]) -> List[str]:
        """
        Determine which screeners to administer based on presenting symptoms
        
        Args:
            symptoms: Dictionary of symptom flags (e.g., {"depression": True, "anxiety": True})
            
        Returns:
            List of screener names to administer
        """
        screeners = []
        
        # =================================================================
        # DEPRESSION & MOOD
        # =================================================================
        if symptoms.get("depression") or symptoms.get("mood"):
            screeners.append("PHQ-9")          # Primary depression
            screeners.append("C-SSRS")         # Suicide risk
            screeners.append("RRS-10")         # Rumination (contributes to depression)
            screeners.append("MDQ")            # MDQ gate for bipolar screening when depression present
        
        # =================================================================
        # ANXIETY
        # =================================================================
        if symptoms.get("anxiety") or symptoms.get("worry"):
            screeners.append("GAD-7")          # Generalized anxiety
            screeners.append("PSWQ-8")         # Worry specifically
        
        # Panic symptoms
        if symptoms.get("panic"):
            screeners.append("PDSS")           # Panic disorder severity
            if "GAD-7" not in screeners:
                screeners.append("GAD-7")      # General anxiety
        
        # Social anxiety
        if symptoms.get("social_anxiety") or symptoms.get("social"):
            screeners.append("SPIN")           # Social phobia
        
        # =================================================================
        # BIPOLAR & MANIA
        # =================================================================
        if symptoms.get("mania") or symptoms.get("hyper") or symptoms.get("energy") or symptoms.get("racing"):
            screeners.append("MDQ")            # Bipolar screening
        
        # =================================================================
        # ADHD & ATTENTION
        # =================================================================
        if symptoms.get("attention") or symptoms.get("focus") or symptoms.get("concentration"):
            screeners.append("ASRS")           # ADHD
        
        # =================================================================
        # TRAUMA & PTSD
        # =================================================================
        if symptoms.get("trauma") or symptoms.get("nightmares") or symptoms.get("flashbacks"):
            screeners.append("PCL-5")          # Full PTSD
            screeners.append("PC-PTSD-5")      # Brief PTSD
            # Add childhood trauma if appropriate
            if symptoms.get("childhood"):
                screeners.append("CTQ-SF")     # Childhood trauma
            # Always include suicide risk if PTSD present
            if "C-SSRS" not in screeners:
                screeners.append("C-SSRS")
        
        # =================================================================
        # SLEEP
        # =================================================================
        if symptoms.get("sleep") or symptoms.get("insomnia") or symptoms.get("tired"):
            screeners.append("ISI")            # Insomnia
        
        # =================================================================
        # SUBSTANCE USE
        # =================================================================
        # Alcohol
        if symptoms.get("substance") or symptoms.get("alcohol") or symptoms.get("drinking"):
            screeners.append("AUDIT-C")        # Alcohol screening
            screeners.append("DAST-10")        # Drug abuse screening
            screeners.append("CAGE-AID")       # Brief substance screen
        
        # Drugs
        if symptoms.get("drugs") or symptoms.get("marijuana") or symptoms.get("cocaine"):
            if "DAST-10" not in screeners:
                screeners.append("DAST-10")    # Drug abuse
            if "CAGE-AID" not in screeners:
                screeners.append("CAGE-AID")   # Brief screen
        
        # =================================================================
        # EATING DISORDERS
        # =================================================================
        if symptoms.get("eating") or symptoms.get("weight") or symptoms.get("food"):
            screeners.append("SCOFF")          # Eating disorders
        
        # =================================================================
        # OCD
        # =================================================================
        if symptoms.get("obsessions") or symptoms.get("compulsions") or symptoms.get("rituals"):
            screeners.append("OCI-R")          # OCD
        
        # =================================================================
        # STRESS
        # =================================================================
        if symptoms.get("stress") or symptoms.get("overwhelmed"):
            screeners.append("PSS-10")         # Perceived stress (full)
            screeners.append("PSS-4")          # Perceived stress (brief)
        
        # =================================================================
        # SOMATIC SYMPTOMS
        # =================================================================
        if symptoms.get("physical") or symptoms.get("pain") or symptoms.get("somatic"):
            screeners.append("PHQ-15")         # Somatic symptoms
        
        # =================================================================
        # FUNCTIONING & DISABILITY
        # =================================================================
        # Always add functional assessment for comprehensive evaluation
        screeners.append("WHODAS 2.0")     # Disability assessment
        
        if symptoms.get("functioning") or symptoms.get("disability") or symptoms.get("work") or symptoms.get("social"):
            screeners.append("WSAS")           # Work/social adjustment
        
        # =================================================================
        # QUALITY OF LIFE
        # =================================================================
        if symptoms.get("loneliness") or symptoms.get("satisfaction") or symptoms.get("quality"):
            screeners.append("UCLA-3")         # Loneliness
            screeners.append("SWLS")           # Life satisfaction
        
        # =================================================================
        # IMPULSIVITY (if relevant symptoms)
        # =================================================================
        if symptoms.get("impulsive") or symptoms.get("reckless"):
            screeners.append("BIS-15")         # Impulsivity
        
        # =================================================================
        # PERINATAL (if applicable)
        # =================================================================
        if symptoms.get("pregnant") or symptoms.get("postpartum") or symptoms.get("perinatal"):
            screeners.append("EPDS")           # Perinatal depression
            if "C-SSRS" not in screeners:
                screeners.append("C-SSRS")     # Suicide risk (critical in perinatal)
        
        # =================================================================
        # DEFAULT BASELINE (if no symptoms detected)
        # =================================================================
        if not screeners:
            screeners = ["PHQ-2", "GAD-2", "C-SSRS"]  # Brief baseline screening
        
        return screeners


# Global registry instance
screener_registry = ScreenerRegistry()

