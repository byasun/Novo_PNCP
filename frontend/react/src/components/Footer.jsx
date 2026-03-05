import React from "react";

// Componente de rodapé da aplicação.
// Props:
// - className: classes CSS adicionais
// - children: conteúdo do rodapé
// - ...props: demais props do elemento footer
const Footer = ({ className = "", children, ...props }) => (
  <footer className={`footer ${className}`.trim()} {...props}>
    {children}
  </footer>
);

export default Footer;
