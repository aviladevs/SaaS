import Layout from "../components/Layout";
import ServiceCard from "../components/ServiceCard";
import { Spa, HeartPulse, Sparkles } from "lucide-react";

export default function Servicos() {
  return (
    <Layout>
      <main className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <ServiceCard
          title="Massagem Relaxante"
          description="Sessão de 60 minutos para aliviar tensões e renovar suas energias."
          icon={<Spa />}
        />
        <ServiceCard
          title="Drenagem Linfática"
          description="Tratamento estético de 50 minutos para melhorar a circulação e eliminar toxinas."
          icon={<HeartPulse />}
        />
        <ServiceCard
          title="Estética Facial"
          description="Cuidados avançados de 45 minutos para realçar sua beleza natural."
          icon={<Sparkles />}
        />
      </main>
    </Layout>
  );
}
