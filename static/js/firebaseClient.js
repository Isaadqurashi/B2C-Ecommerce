// firebaseClient.js

// 1. Import the bits you need from the web SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-analytics.js";
import {
  getFirestore,
  doc,
  getDoc,
  setDoc
} from "https://www.gstatic.com/firebasejs/9.22.1/firebase-firestore.js";

// 2. Paste in your project’s config
const firebaseConfig = {
  apiKey: "AIzaSyD7ToTeU2xiUeXDl4Y3izMYZF8RkdwNnLU",
  authDomain: "kuchu-muchu.firebaseapp.com",
  projectId: "kuchu-muchu",
  storageBucket: "kuchu-muchu.firebasestorage.app",
  messagingSenderId: "651497383206",
  appId: "1:651497383206:web:458bf2f339daace5d20de7",
  measurementId: "G-FDNR426Q2N"
};

// 3. Initialize Firebase & services
const app       = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db        = getFirestore(app);

// 4. Helper functions for Firestore
export async function readUser(uid) {
  const reference = doc(db, "users", uid);
  const snap      = await getDoc(reference);
  if (!snap.exists()) throw new Error("No such user!");
  return snap.data();
}

export async function writeUser(uid, data) {
  await setDoc(doc(db, "users", uid), data);
  return uid;
}

// 5. (Optional) You can export more helpers as you build ’em
export { app, analytics, db };
