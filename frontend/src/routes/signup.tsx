import { zodResolver } from "@hookform/resolvers/zod"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"
import { AuthLayout } from "@/components/Common/AuthLayout"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import i18n from "@/i18n"

const formSchema = z
  .object({
    email: z.email({ message: i18n.t("common:validation.emailInvalid") }),
    full_name: z
      .string()
      .min(1, { message: i18n.t("common:validation.fullNameRequired") }),
    password: z
      .string()
      .min(1, { message: i18n.t("common:validation.passwordRequired") })
      .min(8, { message: i18n.t("common:validation.passwordMinLength") }),
    confirm_password: z.string().min(1, {
      message: i18n.t("common:validation.passwordConfirmationRequired"),
    }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: i18n.t("common:validation.passwordsDontMatch"),
    path: ["confirm_password"],
  })

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: i18n.t("auth:signup.pageTitle"),
      },
    ],
  }),
})

function SignUp() {
  const { t } = useTranslation("auth")
  const { signUpMutation } = useAuth()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  })

  const onSubmit = (data: FormData) => {
    if (signUpMutation.isPending) return

    // exclude confirm_password from submission data
    const { confirm_password: _confirm_password, ...submitData } = data
    signUpMutation.mutate(submitData)
  }

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">{t("signup.title")}</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("signup.fullNameLabel")}</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="full-name-input"
                      placeholder={t("signup.fullNamePlaceholder")}
                      type="text"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("signup.emailLabel")}</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder={t("signup.emailPlaceholder")}
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("signup.passwordLabel")}</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder={t("signup.passwordPlaceholder")}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirm_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("signup.confirmPasswordLabel")}</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="confirm-password-input"
                      placeholder={t("signup.confirmPasswordPlaceholder")}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              className="w-full"
              loading={signUpMutation.isPending}
            >
              {t("signup.submit")}
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            {t("signup.alreadyHaveAccount")}{" "}
            <RouterLink to="/login" className="underline underline-offset-4">
              {t("signup.logInLink")}
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
