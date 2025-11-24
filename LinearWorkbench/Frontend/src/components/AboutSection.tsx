import { motion } from 'motion/react';
import { Info, Users, GraduationCap, Heart } from 'lucide-react';
import { fadeInUp, staggerContainer, staggerItem } from '../utils/animations';

export default function AboutSection() {
  const teamMembers = [
    'Jairo Vega',
    'Jeff Walters',
    'Leana Cruz',
    'Alex Silva'
  ];

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto">
      <div className="space-y-8">
        {/* Header */}
        <motion.div 
          className="text-center space-y-3"
          {...fadeInUp}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Info className="w-8 h-8 text-purple-400" />
            <h2 className="text-3xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Acerca de LinearWorkbench
            </h2>
          </div>
        </motion.div>

        {/* Misión */}
        <motion.div
          className="bg-gradient-to-br from-purple-900/20 to-cyan-900/20 rounded-2xl p-8 border border-purple-500/30"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <p className="text-cyan-100/90 leading-relaxed text-center text-lg">
            Esta herramienta nace con el objetivo de facilitar el aprendizaje y la comprensión 
            profunda del <span className="text-purple-400">Álgebra Lineal</span>, permitiendo a los estudiantes visualizar no solo 
            los resultados, sino el <span className="text-cyan-400">procedimiento lógico</span> detrás de cada operación matricial 
            y vectorial.
          </p>
        </motion.div>

        {/* Equipo de Desarrollo */}
        <motion.div
          className="bg-[#0d0d12]/50 rounded-2xl p-8 border border-purple-500/20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Users className="w-6 h-6 text-purple-400" />
            <h3 className="text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Equipo de Desarrollo
            </h3>
          </div>
          
          <p className="text-cyan-100/80 mb-6">
            Este proyecto fue diseñado y programado por:
          </p>

          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
            variants={staggerContainer}
            initial="hidden"
            animate="show"
          >
            {teamMembers.map((member, index) => (
              <motion.div
                key={index}
                className="bg-gradient-to-r from-purple-900/30 to-cyan-900/30 rounded-lg p-4 border border-purple-500/20 hover:border-purple-400/40 transition-all"
                variants={staggerItem}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                    <span className="text-white">
                      {member.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <span className="text-cyan-100 text-lg">{member}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Desarrollo Académico */}
        <motion.div
          className="bg-[#0d0d12]/50 rounded-2xl p-8 border border-cyan-500/20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center gap-3 mb-6">
            <GraduationCap className="w-6 h-6 text-cyan-400" />
            <h3 className="text-2xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Desarrollo Académico
            </h3>
          </div>
          
          <p className="text-cyan-100/90 leading-relaxed">
            La aplicación fue creada como proyecto final para el curso de{' '}
            <span className="text-purple-400">Álgebra Lineal</span> en la{' '}
            <span className="text-cyan-400">Universidad Americana</span>, integrando 
            la robustez lógica de Python en el backend con la interactividad moderna de React 
            para su apartado visual.
          </p>
        </motion.div>

        {/* Dedicatoria */}
        <motion.div
          className="bg-gradient-to-br from-pink-900/20 via-purple-900/20 to-cyan-900/20 rounded-2xl p-8 border border-pink-500/30 relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {/* Background decoration */}
          <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <Heart className="w-6 h-6 text-pink-400 fill-pink-400/20" />
              <h3 className="text-2xl text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400">
                Dedicatoria
              </h3>
            </div>
            
            <div className="space-y-4">
              <p className="text-cyan-100/90 leading-relaxed">
                Dedicamos este trabajo con especial gratitud a nuestro docente,{' '}
                <span className="text-pink-400">Jose Munguia</span>.
              </p>
              
              <p className="text-cyan-100/80 leading-relaxed italic">
                Gracias por su paciencia, por transmitirnos su pasión por las matemáticas 
                y por enseñarnos todo lo que sabemos sobre el álgebra lineal. Su guía fue 
                fundamental para hacer realidad este proyecto.
              </p>
            </div>

            {/* Decorative hearts */}
            <div className="flex justify-center gap-2 mt-6 opacity-40">
              <Heart className="w-4 h-4 text-pink-400 fill-pink-400" />
              <Heart className="w-4 h-4 text-purple-400 fill-purple-400" />
              <Heart className="w-4 h-4 text-cyan-400 fill-cyan-400" />
            </div>
          </div>
        </motion.div>

        {/* Footer note */}
        <motion.div
          className="text-center text-cyan-400/50 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p>LinearWorkbench • Universidad Americana • 2025</p>
        </motion.div>
      </div>
    </div>
  );
}