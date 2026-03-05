import React from "react";

// Componente de cartão (container visual).
// Props:
// - className: classes CSS adicionais
// - children: conteúdo do cartão
// - ...props: demais props do elemento div
const Card = ({ className = "", children, ...props }) => (
  <div className={`card ${className}`.trim()} {...props}>
    {children}
  </div>
);

export default Card;
