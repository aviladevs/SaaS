import { useState } from "react";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Login tentado com: ${email} / ${senha}`);
    // Aqui depois conecta com a API Django (autenticação JWT)
  };

  return (
    <div className="bg-animated min-h-screen flex items-center justify-center">
      {/* Overlay para legibilidade */}
      <div className="backdrop-blur-md bg-black/60 p-10 rounded-2xl shadow-glow w-full max-w-md">
        <h1 className="text-3xl font-bold text-primary text-center mb-6">
          Espaço Karen Martins
        </h1>
        <p className="text-accent text-center mb-8">
          Acesso restrito ao painel administrativo
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 rounded bg-gray-900 border border-pink-500/30 text-accent focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
          <input
            type="password"
            placeholder="Senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="w-full p-3 rounded bg-gray-900 border border-pink-500/30 text-accent focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
          <button
            type="submit"
            className="w-full py-3 bg-primary text-secondary font-bold rounded-lg shadow-glow hover:scale-105 transition"
          >
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}
