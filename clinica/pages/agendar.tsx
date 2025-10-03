import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { CheckCircle, Clock, Shield, Gift, Info, Loader2 } from "lucide-react";

// Service types and their details
const SERVICES = [
  {
    id: "relaxante",
    name: "Massagem Relaxante",
    duration: 60,
    price: 120,
    description: "Alívio do estresse e renovação das energias",
    popular: true
  },
  {
    id: "drenagem",
    name: "Drenagem Linfática",
    duration: 50,
    price: 100,
    description: "Redução de medidas e melhora na circulação"
  },
  {
    id: "facial",
    name: "Estética Facial",
    duration: 45,
    price: 90,
    description: "Pele renovada e radiante"
  },
  {
    id: "combo1",
    name: "Combo Relaxamento Total",
    duration: 110,
    price: 190,
    description: "Massagem Relaxante + Estética Facial",
    popular: true,
    discount: 15 // % de desconto
  }
];

// Available time slots
const TIME_SLOTS = [
  "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"
];

type FormData = {
  nome: string;
  email: string;
  whatsapp: string;
  servico: string;
  data: string;
  horario: string;
  mensagem: string;
  promocional: boolean;
};

export default function Agendar() {
  const [formData, setFormData] = useState<FormData>({
    nome: "",
    email: "",
    whatsapp: "",
    servico: "",
    data: "",
    horario: "",
    mensagem: "",
    promocional: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [availableTimes, setAvailableTimes] = useState<string[]>([]);
  const [selectedService, setSelectedService] = useState<any>(null);

  // Update available times when date changes
  useEffect(() => {
    if (formData.data) {
      // In a real app, this would check against booked appointments
      setAvailableTimes(TIME_SLOTS);
    }
  }, [formData.data]);

  // Update selected service details
  useEffect(() => {
    if (formData.servico) {
      const service = SERVICES.find(s => s.id === formData.servico);
      setSelectedService(service || null);
    } else {
      setSelectedService(null);
    }
  }, [formData.servico]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const formatPhoneNumber = (value: string) => {
    // Simple phone formatting
    const cleaned = value.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{0,2})(\d{0,5})(\d{0,4})$/);
    if (match) {
      return !match[2] 
        ? `(${match[1]}` 
        : `(${match[1]}) ${match[2]}${match[3] ? `-${match[3]}` : ''}`;
    }
    return value;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value);
    setFormData(prev => ({
      ...prev,
      whatsapp: formatted
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Format the data for the API
      const payload = {
        ...formData,
        whatsapp: formData.whatsapp.replace(/\D/g, ''), // Remove formatting
        data_hora: `${formData.data}T${formData.horario}:00`
      };

      // In a real app, you would send this to your backend
      console.log('Scheduling appointment:', payload);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Success
      setIsSuccess(true);
      
      // Reset form after success
      setFormData({
        nome: "",
        email: "",
        whatsapp: "",
        servico: "",
        data: "",
        horario: "",
        mensagem: "",
        promocional: false
      });
      
      // Reset success message after 5 seconds
      setTimeout(() => setIsSuccess(false), 5000);
      
    } catch (error) {
      console.error('Error scheduling appointment:', error);
      alert('Ocorreu um erro ao agendar. Por favor, tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate next available dates (next 14 days)
  const getAvailableDates = () => {
    const dates = [];
    const today = new Date();
    
    for (let i = 1; i <= 14; i++) {
      const date = new Date();
      date.setDate(today.getDate() + i);
      // Skip Sundays (0) and Saturdays (6)
      if (date.getDay() !== 0 && date.getDay() !== 6) {
        dates.push(date);
      }
    }
    
    return dates;
  };

  // Format date for display
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('pt-BR', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  // Format date for input[type="date"]
  const formatDateForInput = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  return (
    <Layout>
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
              Agende seu momento de bem-estar
            </h1>
            <p className="text-xl text-gray-300">
              Preencha o formulário abaixo para garantir seu horário no Espaço Karen Martins
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Service Selection */}
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold text-primary">Nossos Serviços</h2>
              
              <div className="space-y-4">
                {SERVICES.map((service) => (
                  <div 
                    key={service.id}
                    onClick={() => setFormData(prev => ({ ...prev, servico: service.id }))}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.servico === service.id 
                        ? 'border-primary bg-primary/10' 
                        : 'border-gray-700 hover:border-primary/50'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{service.name}</h3>
                        <p className="text-sm text-gray-400">{service.description}</p>
                        <div className="flex items-center mt-2 text-sm text-gray-300">
                          <Clock className="w-4 h-4 mr-1" />
                          <span>{service.duration} minutos</span>
                          <span className="mx-2">•</span>
                          <span className="font-medium">R$ {service.price}</span>
                          {service.discount && (
                            <span className="ml-2 text-xs bg-green-900 text-green-300 px-2 py-0.5 rounded-full">
                              {service.discount}% OFF
                            </span>
                          )}
                        </div>
                      </div>
                      {service.popular && (
                        <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded-full">
                          Popular
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Benefits */}
              <div className="mt-8 p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                <h3 className="font-medium text-lg mb-4">Por que agendar conosco?</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                    <span>Profissionais especializados</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                    <span>Ambiente climatizado e acolhedor</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                    <span>Produtos de alta qualidade</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                    <span>Horários flexíveis</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Booking Form */}
            <div className="lg:col-span-2">
              <div className="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
                <div className="p-6 border-b border-gray-700">
                  <h2 className="text-2xl font-semibold text-primary">
                    {selectedService ? `Agendar ${selectedService.name}` : 'Selecione um serviço'}
                  </h2>
                  {selectedService && (
                    <p className="text-gray-400 mt-1">
                      {selectedService.duration} minutos • R$ {selectedService.price}
                      {selectedService.discount && (
                        <span className="ml-2 text-sm bg-green-900/50 text-green-300 px-2 py-0.5 rounded-full">
                          {selectedService.discount}% de desconto
                        </span>
                      )}
                    </p>
                  )}
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                  {isSuccess ? (
                    <div className="bg-green-900/30 border border-green-800 text-green-300 p-4 rounded-lg text-center">
                      <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-400" />
                      <h3 className="text-xl font-semibold mb-2">Agendamento Confirmado!</h3>
                      <p>Entraremos em contato em breve para confirmar os detalhes.</p>
                      <p className="mt-2 text-sm text-green-200">Obrigado por escolher o Espaço Karen Martins!</p>
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="nome" className="block text-sm font-medium text-gray-300 mb-1">
                            Nome completo *
                          </label>
                          <input
                            type="text"
                            id="nome"
                            name="nome"
                            value={formData.nome}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            placeholder="Seu nome completo"
                            required
                          />
                        </div>

                        <div>
                          <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
                            E-mail *
                          </label>
                          <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            placeholder="seu@email.com"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-300 mb-1">
                            WhatsApp *
                          </label>
                          <input
                            type="tel"
                            id="whatsapp"
                            name="whatsapp"
                            value={formData.whatsapp}
                            onChange={handlePhoneChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            placeholder="(00) 00000-0000"
                            required
                          />
                        </div>

                        <div>
                          <label htmlFor="servico" className="block text-sm font-medium text-gray-300 mb-1">
                            Serviço *
                          </label>
                          <select
                            id="servico"
                            name="servico"
                            value={formData.servico}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            required
                          >
                            <option value="">Selecione um serviço</option>
                            {SERVICES.map(service => (
                              <option key={service.id} value={service.id}>
                                {service.name} - {service.duration}min (R$ {service.price})
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="data" className="block text-sm font-medium text-gray-300 mb-1">
                            Data *
                          </label>
                          <select
                            id="data"
                            name="data"
                            value={formData.data}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            required
                          >
                            <option value="">Selecione uma data</option>
                            {getAvailableDates().map((date, index) => (
                              <option key={index} value={formatDateForInput(date)}>
                                {formatDate(date)}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label htmlFor="horario" className="block text-sm font-medium text-gray-300 mb-1">
                            Horário *
                          </label>
                          <select
                            id="horario"
                            name="horario"
                            value={formData.horario}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                            disabled={!formData.data}
                            required
                          >
                            <option value="">Selecione um horário</option>
                            {availableTimes.map((time, index) => (
                              <option key={index} value={time}>
                                {time}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div>
                        <label htmlFor="mensagem" className="block text-sm font-medium text-gray-300 mb-1">
                          Mensagem (opcional)
                        </label>
                        <textarea
                          id="mensagem"
                          name="mensagem"
                          value={formData.mensagem}
                          onChange={handleInputChange}
                          rows={3}
                          className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-primary/50 focus:border-primary transition"
                          placeholder="Alguma observação ou necessidade especial?"
                        />
                      </div>

                      <div className="flex items-start">
                        <div className="flex items-center h-5">
                          <input
                            id="promocional"
                            name="promocional"
                            type="checkbox"
                            checked={formData.promocional}
                            onChange={handleInputChange}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 focus:ring-primary/50"
                          />
                        </div>
                        <label htmlFor="promocional" className="ml-3 text-sm text-gray-300">
                          Desejo receber ofertas e novidades por e-mail
                        </label>
                      </div>

                      <div className="pt-2">
                        <button
                          type="submit"
                          disabled={isLoading}
                          className={`w-full flex justify-center items-center py-4 px-6 bg-gradient-to-r from-primary to-primary/80 text-white font-semibold rounded-lg hover:opacity-90 transition-all ${
                            isLoading ? 'opacity-80 cursor-not-allowed' : ''
                          }`}
                        >
                          {isLoading ? (
                            <>
                              <Loader2 className="animate-spin mr-2 h-5 w-5" />
                              Processando...
                            </>
                          ) : (
                            'Confirmar Agendamento'
                          )}
                        </button>
                      </div>

                      <div className="text-center text-xs text-gray-400 mt-4">
                        <p className="flex items-center justify-center">
                          <Shield className="w-4 h-4 mr-1" />
                          Seus dados estão seguros conosco
                        </p>
                      </div>
                    </>
                  )}
                </form>
              </div>

              {/* Trust Badges */}
              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="w-10 h-10 mx-auto mb-2 flex items-center justify-center text-primary">
                    <Shield className="w-6 h-6" />
                  </div>
                  <p className="text-sm font-medium">Dados Seguros</p>
                </div>
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="w-10 h-10 mx-auto mb-2 flex items-center justify-center text-primary">
                    <Clock className="w-6 h-6" />
                  </div>
                  <p className="text-sm font-medium">Agendamento Rápido</p>
                </div>
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="w-10 h-10 mx-auto mb-2 flex items-center justify-center text-primary">
                    <Gift className="w-6 h-6" />
                  </div>
                  <p className="text-sm font-medium">Ofertas Exclusivas</p>
                </div>
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="w-10 h-10 mx-auto mb-2 flex items-center justify-center text-primary">
                    <Info className="w-6 h-6" />
                  </div>
                  <p className="text-sm font-medium">Suporte 24/7</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
