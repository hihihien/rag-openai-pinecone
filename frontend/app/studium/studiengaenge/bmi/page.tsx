import Chatbot from "@/app/components/Chatbot";

export default function BMIPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>Bachelor (B.Sc.) Medieninformatik</h1>
      <p>
        Willkommen auf der Informationsseite zum Bachelorstudiengang Medieninformatik (BMI) am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="BMI" />
    </main>
  );
}