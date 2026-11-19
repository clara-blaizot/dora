import { useEffect, useState } from "react";
import { createSubject, listSubjects } from "../api.js";

// Les matières sont stockées dans le backend. Ce hook les charge et en crée.
const COLORS = ["#D6336C", "#F783AC", "#A61E4D", "#E599B8", "#F06595", "#C2255C"];

// Chargement partagé : en développement, React exécute les effets deux fois
// (StrictMode). Sans ça, on créerait deux « Ma matière » au premier lancement.
let chargement = null;

function chargerMatieres() {
  chargement ??= listSubjects()
    .then(async (list) => {
      // Premier lancement : on crée une matière pour ne pas partir d'un écran vide
      if (list.length === 0) list = [await createSubject("Ma matière", COLORS[0])];
      return list;
    })
    .catch((err) => {
      chargement = null; // permettre un nouvel essai au prochain affichage
      throw err;
    });
  return chargement;
}

export function useSubjects() {
  const [subjects, setSubjects] = useState([]);
  const [status, setStatus] = useState("loading"); // "loading" | "ready" | "error"

  useEffect(() => {
    chargerMatieres()
      .then((list) => {
        setSubjects(list);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  async function addSubject(name) {
    const subject = await createSubject(name, COLORS[subjects.length % COLORS.length]);
    setSubjects((list) => [...list, subject]);
    return subject;
  }

  return { subjects, status, addSubject };
}
