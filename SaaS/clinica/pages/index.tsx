import Layout from "../components/Layout";
import Link from "next/link";

export default function Home() {
  return (
    <Layout>
      <section className="flex-1 flex flex-col justify-center items-center text-center p-8">
        <h2 className="text-5xl font-bold text-primary">
          Bem-vindo ao Espaço Karen Martins
        </h2>
        <p className="mt-4 text-lg max-w-xl">
          Massoterapia e estética em um ambiente premium, pensado para o seu
          bem-estar.
        </p>
        <Link href="/agendar">
          <button className="mt-8 px-6 py-3 bg-primary text-secondary font-semibold rounded-lg shadow-premium hover:scale-105 transition">
            Agende sua experiência
          </button>
        </Link>
      </section>
    </Layout>
  );
}
