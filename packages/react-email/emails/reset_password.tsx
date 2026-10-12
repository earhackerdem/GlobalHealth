import { Text } from "@react-email/components"
import { LinkButton } from "../ui/Button"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"
import { Link } from "../ui/Link"

type ResetPasswordProps = {
  project_name: string
  username: string
  link: string
  valid_hours: string
}

export default function ResetPassword({
  project_name = "{{ project_name }}",
  username = "{{ username }}",
  link = "{{ link }}",
  valid_hours = "{{ valid_hours }}",
}: ResetPasswordProps) {
  return (
    <Layout
      title={`${project_name} - Recuperación de contraseña`}
      preview={`Restablece tu contraseña de ${project_name}`}
      project_name={project_name}
    >
      <Heading>Restablece tu contraseña</Heading>
      <Text style={bodyTextStyle}>Hola {username}:</Text>
      <Text style={bodyTextStyle}>
        Recibimos una solicitud para restablecer tu contraseña de{" "}
        {project_name}. Elige una nueva con el botón de abajo:
      </Text>
      <LinkButton href={link}>Restablecer contraseña</LinkButton>
      <Text style={supportingTextStyle}>
        O copia y pega este enlace en tu navegador:
        <br />
        <Link href={link}>{link}</Link>
      </Text>
      <Text style={supportingTextStyle}>
        Este enlace expira en {valid_hours} hora(s).
      </Text>
      <Text style={supportingTextStyle}>
        Si no solicitaste recuperar tu contraseña, puedes ignorar este correo
        con tranquilidad.
      </Text>
    </Layout>
  )
}

const bodyTextStyle = {
  color: "#334155",
  fontSize: "15px",
  lineHeight: "26px",
  margin: "0 0 18px",
}

const supportingTextStyle = {
  color: "#64748b",
  fontSize: "14px",
  lineHeight: "23px",
  margin: "0 0 16px",
}
