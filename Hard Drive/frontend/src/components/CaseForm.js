// File: /Users/rick/CaseProject/frontend/src/components/CaseForm.js
import React, { useState } from 'react';

const CaseForm = ({ onSubmit, isSubmitting }) => {
  // State for the form fields
  const [court, setCourt] = useState("");
  const [date, setDate] = useState("");
  const [plaintiffMedicalExpert, setPlaintiffMedicalExpert] = useState("");
  const [defenseMedicalExpert, setDefenseMedicalExpert] = useState("");
  const [plaintiffExpert, setPlaintiffExpert] = useState("");
  const [defenseExpert, setDefenseExpert] = useState("");
  const [judgeArbitratorMediator, setJudgeArbitratorMediator] = useState("");
  const [insuranceCompany, setInsuranceCompany] = useState("");
  const [claimType, setClaimType] = useState("");
  const [injuryType, setInjuryType] = useState("");
  const [facts, setFacts] = useState("");
  const [injuries, setInjuries] = useState("");
  const [economicDamages, setEconomicDamages] = useState("");

  // Function to validate form
  const validateForm = () => {
    // Required fields: facts, injuries, economicDamages
    if (!facts.trim()) {
      alert("Facts are required");
      return false;
    }
    if (!injuries.trim()) {
      alert("Injuries are required");
      return false;
    }
    if (!economicDamages.trim()) {
      alert("Economic damages are required");
      return false;
    }
    return true;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    // Create case data object
    const caseData = {
      court,
      date,
      plaintiff_medical_expert: plaintiffMedicalExpert,
      defense_medical_expert: defenseMedicalExpert,
      plaintiff_expert: plaintiffExpert,
      defense_expert: defenseExpert,
      judge_arbitrator_mediator: judgeArbitratorMediator,
      insurance_company: insuranceCompany,
      claim_type: claimType,
      injury_type: injuryType,
      facts,
      injuries,
      economic_damages: economicDamages
    };

    // Call the onSubmit function passed from parent component
    onSubmit(caseData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <label>Court:</label>
        <input type="text" value={court} onChange={(e) => setCourt(e.target.value)} />
      </div>
      <div className="form-row">
        <label>Date:</label>
        <input 
          type="text" 
          value={date} 
          onChange={(e) => setDate(e.target.value)} 
          placeholder="YYYY-MM-DD" 
        />
      </div>
      <div className="form-row">
        <label>Plaintiff Medical Expert:</label>
        <input 
          type="text" 
          value={plaintiffMedicalExpert} 
          onChange={(e) => setPlaintiffMedicalExpert(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Defense Medical Expert:</label>
        <input 
          type="text" 
          value={defenseMedicalExpert} 
          onChange={(e) => setDefenseMedicalExpert(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Plaintiff Expert:</label>
        <input 
          type="text" 
          value={plaintiffExpert} 
          onChange={(e) => setPlaintiffExpert(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Defense Expert:</label>
        <input 
          type="text" 
          value={defenseExpert} 
          onChange={(e) => setDefenseExpert(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Judge/Arbitrator/Mediator:</label>
        <input 
          type="text" 
          value={judgeArbitratorMediator} 
          onChange={(e) => setJudgeArbitratorMediator(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Insurance Company:</label>
        <input 
          type="text" 
          value={insuranceCompany} 
          onChange={(e) => setInsuranceCompany(e.target.value)} 
        />
      </div>
      <div className="form-row">
        <label>Claim Type:</label>
        <input type="text" value={claimType} onChange={(e) => setClaimType(e.target.value)} />
      </div>
      <div className="form-row">
        <label>General type of Injury or Damage:</label>
        <input type="text" value={injuryType} onChange={(e) => setInjuryType(e.target.value)} />
      </div>
      <div className="form-row">
        <label>Facts *:</label>
        <textarea value={facts} onChange={(e) => setFacts(e.target.value)} rows="3" />
      </div>
      <div className="form-row">
        <label>Details - Injuries or Damages *:</label>
        <textarea value={injuries} onChange={(e) => setInjuries(e.target.value)} rows="3" />
      </div>
      <div className="form-row">
        <label>Economic Damages *:</label>
        <input 
          type="text" 
          value={economicDamages} 
          onChange={(e) => setEconomicDamages(e.target.value)} 
        />
      </div>
      <p className="required-note">* Indicates required data.</p>
      <div className="button-container">
        <button 
          type="submit" 
          className="analyze-button" 
          disabled={isSubmitting}
        >
          {isSubmitting ? "Analyzing..." : "Analyze Case"}
        </button>
      </div>
    </form>
  );
};

export default CaseForm;
