import { Form } from "@/components/composed_ui/Form";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const signUpSchema = z.object({
  email: z
    .string()
    .email("Введіть адресу електронної пошти у форматі name@example.com"),
  password: z.string().min(6, "Електронна пошта чи пароль вказані некоректно"),
});

export type SignUpFormValues = z.infer<typeof signUpSchema>;

export function SignUp() {
  const form = useForm<SignUpFormValues>({
    resolver: zodResolver(signUpSchema),
    mode: "onChange",
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const { isValid, isSubmitting } = form.formState;

  const handleSignUp = async (data: SignUpFormValues) => {
    try {
      console.log(data);
    } catch (error: unknown) {
      form.setError("password", {
        type: "manual",
        message: error instanceof Error ? error.message : "Невідома помилка",
      });
    }
  };

  return (
    <div className="px-2 mx-auto flex items-center justify-center h-screen">
      <Form form={form} onSubmit={handleSignUp}>
        <Form.Header title="Реєстрація" />
        <Form.Body>
        </Form.Body>
        <Form.Footer>
          <Button disabled={!isValid || isSubmitting}>Зареєструватися</Button>
        </Form.Footer>
      </Form>
    </div>
  );
}
