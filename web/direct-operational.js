function signed(policy,value){
  if(policy.action==="DECREASE") return -Math.abs(value);
  return Math.abs(value);
}

function firstNumber(text){
  const match=text.match(/(\d[\d\s]*(?:[,.]\d+)?)/);
  if(!match) return null;
  return Number(match[1].replaceAll(" ","").replace(",","."));
}

function explicitUnitValue(text,units){
  const pattern=new RegExp("(\\d[\\d\\s]*(?:[,.]\\d+)?)\\s*("+units.join("|")+")","i");
  const match=text.match(pattern);
  if(!match) return null;
  return {
    value:Number(match[1].replaceAll(" ","").replace(",",".")),
    unit:match[2]
  };
}

export function extractDirectOperationalEffects(policies){
  const effects=[];

  for(const policy of policies){
    const text=policy.text.toLowerCase();
    const count=firstNumber(text);
    if(count==null) continue;

    const staffPatterns=[
      {re:/policiers?|gendarmes?/,indicator:"security",label:"Effectifs de police / gendarmerie",unit:"agents"},
      {re:/professeurs?|enseignants?/,indicator:"education",label:"Effectifs enseignants",unit:"agents"},
      {re:/soignants?|infirmiers?|médecins?|medecins?/,indicator:"health",label:"Effectifs de santé",unit:"agents"},
      {re:/magistrats?|juges?|greffiers?/,indicator:"security",label:"Effectifs de justice",unit:"agents"}
    ];

    if(/recruter|embaucher|créer\s+\d|creer\s+\d|supprimer\s+\d|réduire\s+de\s+\d|reduire\s+de\s+\d/.test(text)){
      const staff=staffPatterns.find(x=>x.re.test(text));
      if(staff){
        effects.push({
          kind:"staffing",
          indicator:staff.indicator,
          label:staff.label,
          value:signed(policy,count),
          unit:staff.unit,
          sourceText:policy.text,
          confidence:"Calcul direct"
        });
        continue;
      }
    }

    const infrastructurePatterns=[
      {re:/hôpitaux?|hopitaux?|centres? de santé|centres? de sante/,indicator:"health",label:"Capacité hospitalière",unit:"sites"},
      {re:/prisons?|établissements? pénitentiaires?|etablissements? penitentiaires?/,indicator:"security",label:"Infrastructures pénitentiaires",unit:"sites"},
      {re:/écoles?|ecoles?|collèges?|colleges?|lycées?|lycees?/,indicator:"education",label:"Infrastructures scolaires",unit:"sites"},
      {re:/logements?/,indicator:"housing",label:"Logements créés / supprimés",unit:"logements"},
      {re:/gares?|lignes? ferroviaires?|lignes? de train/,indicator:"mobility",label:"Infrastructures de transport",unit:"projets"}
    ];

    if(/construire|créer|creer|ouvrir|fermer|supprimer/.test(text)){
      const infra=infrastructurePatterns.find(x=>x.re.test(text));
      if(infra){
        effects.push({
          kind:"infrastructure",
          indicator:infra.indicator,
          label:infra.label,
          value:signed(policy,count),
          unit:infra.unit,
          sourceText:policy.text,
          confidence:"Calcul direct"
        });
        continue;
      }
    }

    const rail=explicitUnitValue(text,["km","kilomètres?","kilometres?"]);
    if(rail && /rail|ferroviaire|train/.test(text)){
      effects.push({
        kind:"infrastructure",
        indicator:"mobility",
        label:"Réseau ferroviaire",
        value:signed(policy,rail.value),
        unit:"km",
        sourceText:policy.text,
        confidence:"Calcul direct"
      });
      continue;
    }

    const energy=explicitUnitValue(text,["gw","mw"]);
    if(energy && /nucléaire|nucleaire|solaire|éolien|eolien|renouvelable|énergie|energie/.test(text)){
      const unit=energy.unit.toUpperCase();
      effects.push({
        kind:"capacity",
        indicator:"energy",
        label:"Capacité énergétique",
        value:signed(policy,energy.value),
        unit,
        sourceText:policy.text,
        confidence:"Calcul direct"
      });
    }
  }

  return effects;
}

export function groupOperationalEffects(effects){
  return effects.reduce((acc,effect)=>{
    (acc[effect.indicator] ||= []).push(effect);
    return acc;
  },{});
}
