import Chatbot from "@/app/components/Chatbot";

export default function BCSIMPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>B.A. Creative, Synthetic & Interactive Media</h1>
      <p>
        Willkommen auf der Informationsseite zum Bachelorstudiengang Creative, Synthetic & Interactive Media am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="BCSIM" />
    </main>
  );
}